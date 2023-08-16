#!/bin/sh
# Start in the directory containing the `vse-sync-test` and `vse-sync-collection-tools` repositories.
set -e
# defaults
DURATION=2000s

usage() {
	read -d '' usage_prompt <<- EOF
	Usage: $0 -k KUBECONFIG [-i INTERFACE_NAME] [-d DURATION]

    Options (required):
        -k: Path to the kubeconfig to be used

    Options (optional):
        -i: name of the interface to gather data about
        -d: How many seconds to run data collection.
    
    Example Usage:
        $0 -k ~/kubeconfig

	EOF

	echo -e "$usage_prompt"
}

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

    DATADIR=$TESTROOT/data
    RESULTSDIR=$DATADIR/results

    mkdir -p $DATADIR 
    mkdir -p $RESULTSDIR

    ENVJSON="${RESULTSDIR}/env.json"
    TESTJSON="${RESULTSDIR}/test.json"

    ENVADOC="${RESULTSDIR}/env.adoc"
    TESTADOC="${RESULTSDIR}/test.adoc"

    ENVJUNIT="${RESULTSDIR}/env.junit"
    TESTJUNIT="${RESULTSDIR}/test.junit"
    FULLJUNIT="${RESULTSDIR}/combined.junit"
}

verify_env(){
  echo "Verifying test env. Please wait..."
  cd $COLLECTORPATH
  dt=$(date --rfc-3339='seconds' -u)
  junit_template=$(echo ".[].data + { \"timestamp\": \"${dt}\", "time": 0}")
  go run main.go env verify --interface="${INTERFACE_NAME}" --kubeconfig="${LOCAL_KUBECONFIG}" --use-analyser-format >> ${ENVJSON}.raw
  cat ${ENVJSON}.raw | jq -s -c "${junit_template}" >> ${ENVJSON}
}

collect_data() {
    echo "Collecting $DURATION of data. Please wait..."
    cd $COLLECTORPATH
    go run main.go collect --interface="${INTERFACE_NAME}" --kubeconfig="${LOCAL_KUBECONFIG}" --output="${DATADIR}/collected.log" --use-analyser-format --duration=${DURATION}
    go run main.go logs -k="${LOCAL_KUBECONFIG}" -o="${DATADIR}" --since="${DURATION}"
}

analyse_data() {
    PTP_DAEMON_LOGFILE=$(ls -tr1 $DATADIR/linuxptp-daemon-container-* | tail -n 1)

    GNSS_DEMUXED_PATH=$DATADIR/gnss-terror.demuxed
    DPLL_DEMUXED_PATH=$DATADIR/dpll-terror.demuxed

    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux  $DATADIR/collected.log 'gnss/time-error' >> $GNSS_DEMUXED_PATH
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux  $DATADIR/collected.log 'dpll/time-error' >> $DPLL_DEMUXED_PATH

    cd ${ANALYSERPATH}
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

check_vars
verify_env
collect_data
analyse_data
create_junit
create_adoc

cat ${FULLJUNIT}
