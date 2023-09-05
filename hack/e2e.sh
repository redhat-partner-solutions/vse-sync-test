#!/bin/sh
# Start from a directory containing each of the repositories:
# `vse-sync-collection-tools`, `vse-sync-test`, `vse-sync-test-report`, and `testdrive`.

set -e
set -o pipefail

# defaults
DURATION=2000s

usage() {
    cat - <<EOF
Usage: $(basename "$0") -k KUBECONFIG [-i INTERFACE_NAME] [-d DURATION]

Arguments:
    -k: path to the kubeconfig to be used

Options (optional):
    -i: name of the interface to gather data about
    -d: how many seconds to run data collection

Example Usage:
    $(basename "$0") -k ~/kubeconfig
EOF
}

# Parge args beginning with -
while [[ $1 == -* ]]; do
    case "$1" in
      -h|--help|-\?) usage; exit 0;;
      -k) if (($# > 1)); then
            export LOCAL_KUBECONFIG=$2; shift 2
          else
            echo "-k requires an argument" 1>&2
            usage
            exit 1
          fi ;;
      -i) if (($# > 1)); then
            export INTERFACE_NAME=$2; shift 2
          else
            echo "-i requires an argument" 1>&2
            usage
            exit 1
          fi ;;
      -d) if (($# > 1)); then
            export DURATION=$2; shift 2
          else
            echo "-d requires an argument" 1>&2
            usage
            exit 1
          fi ;;		  
      --) shift; break;;
      -*) echo "invalid option: $1" 1>&2; usage; exit 1;;
    esac
done

check_vars() {
    local required_vars=('LOCAL_KUBECONFIG')
    local required_vars_err_messages=(
	'KUBECONFIG is invalid or not given. Use the -k option to provide path to kubeconfig file.'
	)
	local var_missing=false

	for index in "${!required_vars[@]}"; do
		var=${required_vars[$index]}
		if [[ -z ${!var} ]]; then
			error_message=${required_vars_err_messages[$index]}
			echo "$0: error: $error_message" 1>&2
			var_missing=true
		fi
	done

	if $var_missing; then
		echo ""
		usage
        exit 1
	fi

    if [[ -z $INTERFACE_NAME ]]; then
        INTERFACE_NAME=$(oc -n openshift-ptp --kubeconfig=${LOCAL_KUBECONFIG} exec daemonset/linuxptp-daemon -c linuxptp-daemon-container -- ls /sys/class/gnss/gnss0/device/net/)
        echo "Discovered interface name: $INTERFACE_NAME"
    else    
        echo "Using interface name: $INTERFACE_NAME"
    fi

    TESTROOT=$(pwd)
    COLLECTORPATH=$TESTROOT/vse-sync-collection-tools
    ANALYSERPATH=$TESTROOT/vse-sync-test
    REPORTGENPATH=$TESTROOT/vse-sync-test-report
    TDPATH=$TESTROOT/testdrive/src
    PPPATH=$ANALYSERPATH/vse-sync-pp/src

    DATADIR=$TESTROOT/data
    RESULTSDIR=$DATADIR/results

    mkdir -p $DATADIR 
    mkdir -p $RESULTSDIR

    ENVJSON="${RESULTSDIR}/env.json"
    TESTJSON="${RESULTSDIR}/test.json"
}

audit_repo() {
  pushd "$1" >/dev/null 2>&1
  cat - << EOF
  {
    "path": "$1",
    "commit": "$(git show -s --format=%H HEAD)",
    "branch": "$(git branch --show-current)",
    "status": "$(git status --short)"
    }
EOF
  popd >/dev/null 2>&1
}

audit_container() {
  cat - << EOF
{
  "vse-sync-collection-tools": $(audit_repo $COLLECTORPATH),
  "vse-sync-test": $(audit_repo $ANALYSERPATH),
  "vse-sync-pp": $(audit_repo $PPPATH),
  "testdrive": $(audit_repo $TDPATH),
  "vse-sync-test-report": $(audit_repo $REPORTGENPATH)
}
EOF
}

verify_env(){
  pushd "$COLLECTORPATH" >/dev/null 2>&1
  echo "Verifying test env. Please wait..."
  dt=$(date --rfc-3339='seconds' -u)
  junit_template=$(echo ".[].data + { \"timestamp\": \"${dt}\", "time": 0}")
  go run main.go env verify --interface="${INTERFACE_NAME}" --kubeconfig="${LOCAL_KUBECONFIG}" --use-analyser-format >> ${ENVJSON}.raw
  cat ${ENVJSON}.raw | jq -s -c "${junit_template}" >> ${ENVJSON}
  popd >/dev/null 2>&1
}

collect_data() {
  pushd "$COLLECTORPATH" >/dev/null 2>&1
  echo "Collecting $DURATION of data. Please wait..."
  go run main.go collect --interface="${INTERFACE_NAME}" --kubeconfig="${LOCAL_KUBECONFIG}" --output="${DATADIR}/collected.log" --use-analyser-format --duration=${DURATION}
  go run main.go logs -k="${LOCAL_KUBECONFIG}" -o="${DATADIR}" --since="${DURATION}"
  popd >/dev/null 2>&1
}

analyse_data() {
  pushd "$ANALYSERPATH" >/dev/null 2>&1
  PTP_DAEMON_LOGFILE=$(ls -tr1 $DATADIR/linuxptp-daemon-container-* | tail -n 1)

  GNSS_DEMUXED_PATH=$DATADIR/gnss-terror.demuxed
  DPLL_DEMUXED_PATH=$DATADIR/dpll-terror.demuxed

  PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux  $DATADIR/collected.log 'gnss/time-error' >> $GNSS_DEMUXED_PATH
  PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux  $DATADIR/collected.log 'dpll/time-error' >> $DPLL_DEMUXED_PATH

  DRIVE_TESTS_JSON="tests.json"
  SPACER="    "
  echo "[" > $DRIVE_TESTS_JSON
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py\", \"${PTP_DAEMON_LOGFILE}\"]," >> $DRIVE_TESTS_JSON
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py\", \"${PTP_DAEMON_LOGFILE}\"]," >> $DRIVE_TESTS_JSON
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/PHC-to-SYS/RAN/testimpl.py\", \"${PTP_DAEMON_LOGFILE}\"]," >> $DRIVE_TESTS_JSON
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/testimpl.py\", \"${GNSS_DEMUXED_PATH}\"]," >> $DRIVE_TESTS_JSON
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/testimpl.py\", \"${GNSS_DEMUXED_PATH}\"]," >> $DRIVE_TESTS_JSON
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-A/testimpl.py\", \"${DPLL_DEMUXED_PATH}\"]," >> $DRIVE_TESTS_JSON
  # Remember to fixup trailing commas if you amend this!
  echo "${SPACER}[\"tests/sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-B/testimpl.py\", \"${DPLL_DEMUXED_PATH}\"]" >> $DRIVE_TESTS_JSON
  echo "]" >> $DRIVE_TESTS_JSON

  BRANCHNAME=$(git branch --show-current)

  env PYTHONPATH=$TDPATH:$PPPATH python3 -m testdrive.run https://github.com/redhat-partner-solutions/vse-sync-test/tree/${BRANCHNAME} $DRIVE_TESTS_JSON >> ${TESTJSON}
  popd >/dev/null 2>&1
}

create_junit() {
  cat ${ENVJSON} | env PYTHONPATH=$TDPATH python3 -m testdrive.junit --prettify "Environment" - >  ${ENVJUNIT}
  cat ${TESTJSON} | env PYTHONPATH=$TDPATH python3 -m testdrive.junit --prettify "T-GM Tests" - >  ${TESTJUNIT}

  junitparser merge ${RESULTSDIR}/*.junit ${FULLJUNIT}
}

create_adoc() {
  cat ${ENVJSON} | env PYTHONPATH=$TDPATH python3 -m testdrive.asciidoc "Environment" - >  ${ENVADOC}
  cat ${TESTJSON} | env PYTHONPATH=$TDPATH python3 -m testdrive.asciidoc "T-GM Tests" - >  ${TESTADOC}
}

check_vars
audit_container > $DATADIR/repo_audit
verify_env
collect_data
analyse_data
create_junit
create_adoc

# Make exit code indicate test results rather than successful completion. 
if grep -Eq '(errors|failures)=\"([^0].*?)\"' $FULLJUNIT
then
    exit 1
else
    exit 0
fi
