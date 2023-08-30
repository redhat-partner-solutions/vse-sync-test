#!/bin/sh
# Start in the directory containing the `vse-sync-test` and `vse-sync-collection-tools` repositories.

set -e
set -o pipefail

# defaults
DURATION=2000s

usage() {
    cat - <<EOF
Usage: $(basename "$0") -k KUBECONFIG [-i INTERFACE_NAME] [-d DURATION]

Options (required):
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
	'KUBECONFIG is invalid or not given. Use the -k option to provide path to one or more kubeconfig files.'
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
    TDPATH=$TESTROOT/testdrive/src
    PPPATH=$ANALYSERPATH/vse-sync-pp/src

    OUTPUTDIR=$TESTROOT/data
    DATADIR=$OUTPUTDIR/collected # Raw collected data/logs
    ARTEFACTDIR=$OUTPUTDIR/artefacts # place mid pipeline files here
    PLOTDIR=$OUTPUTDIR/plots

    mkdir -p $DATADIR
    mkdir -p $ARTEFACTDIR
    mkdir -p $PLOTDIR

    GNSS_DEMUXED_PATH=$ARTEFACTDIR/gnss-terror.demuxed
    DPLL_DEMUXED_PATH=$ARTEFACTDIR/dpll-terror.demuxed

    ENVJSON="${ARTEFACTDIR}/env.json"
    TESTJSON="${ARTEFACTDIR}/test.json"

    ENVADOC="${ARTEFACTDIR}/env.adoc"
    TESTADOC="${ARTEFACTDIR}/test.adoc"

    ENVJUNIT="${ARTEFACTDIR}/env.junit"
    TESTJUNIT="${ARTEFACTDIR}/test.junit"
    FULLJUNIT="${OUTPUTDIR}/results.junit"

    pushd "$ANALYSERPATH" >/dev/null 2>&1
    local commit="$(git show -s --format=%H HEAD)"
    popd >/dev/null 2>&1

    BASEURL_ENV_IDS=https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/
    BASEURL_TEST_IDS=https://docs.engineering.redhat.com/vse-sync-test/
    BASEURL_SPECS=https://github.com/redhat-partner-solutions/vse-sync-test/blob/${COMMIT}/
}

audit_repo() {
  pushd "$1" >/dev/null 2>&1
  cat - << EOF
  {
    "path": "$1",
    "commit": "$(git show -s --format=%H HEAD)",
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
}'
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
  local PTP_DAEMON_LOGFILE=$(ls -tr1 $DATADIR/linuxptp-daemon-container-* | tail -n 1)

  PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $DATADIR/collected.log 'gnss/time-error' >> $GNSS_DEMUXED_PATH
  PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $DATADIR/collected.log 'dpll/time-error' >> $DPLL_DEMUXED_PATH

  cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "${PTP_DAEMON_LOGFILE}"]
["tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "${PTP_DAEMON_LOGFILE}"]
["tests/sync/G.8272/time-error-in-locked-mode/PHC-to-SYS/RAN/testimpl.py", "${PTP_DAEMON_LOGFILE}"]
["tests/sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/testimpl.py", "${GNSS_DEMUXED_PATH}"]
["tests/sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/testimpl.py", "${GNSS_DEMUXED_PATH}"]
["tests/sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-A/testimpl.py", "${DPLL_DEMUXED_PATH}"]
["tests/sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-B/testimpl.py", "${DPLL_DEMUXED_PATH}"]
EOF
  env PYTHONPATH=$TDPATH:$PPPATH python3 -m testdrive.run "$BASEURL_TEST_IDS" --basedir="$ANALYSERPATH" $ARTEFACTDIR/testdrive_config.json
  popd >/dev/null 2>&1
}

create_junit() {
  cat ${ENVJSON} | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit --baseurl-ids="$BASEURL_ENV_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "Environment" - \
        > ${ENVJUNIT}

  cat ${TESTJSON} | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit --baseurl-ids="$BASEURL_TEST_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "T-GM Tests" - \
        > ${TESTJUNIT}

  junitparser merge ${ARTEFACTDIR}/*.junit ${FULLJUNIT}
}

create_charts() {
  env PYTHONPATH=$PPPATH python3 -m vse_sync_pp.plot -c $GNSS_DEMUXED_PATH gnss/time-error $PLOTDIR/gnss-terror.png
  env PYTHONPATH=$PPPATH python3 -m vse_sync_pp.plot -c $DPLL_DEMUXED_PATH dpll/time-error $PLOTDIR/dpll-terror.png
}

create_adoc() {
  cat ${ENVJSON} | env PYTHONPATH=$TDPATH python3 -m testdrive.asciidoc "Environment" - >  ${ENVADOC}
  cat ${TESTJSON} | env PYTHONPATH=$TDPATH python3 -m testdrive.asciidoc "T-GM Tests" - >  ${TESTADOC}
}

check_vars
audit_container > $DATADIR/repo_audit
verify_env
collect_data
analyse_data >"$TESTJSON"
create_junit
create_charts
create_adoc

cat ${FULLJUNIT}
