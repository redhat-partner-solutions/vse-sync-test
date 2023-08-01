#!/bin/sh
# Start in the directory containing the `vse-sync-test` and `vse-sync-collection-tools` repositories.
set -e
# defaults
DURATION=1500s

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
    PPPATH=$ANALYSERPATH/vse-sync-pp/src
    DATADIR=$TESTROOT/data # TODO add timestamp suffix

    mkdir -p $DATADIR 
}

collect_data() {
    echo "Collecting $DURATION of data. Please wait..."
    cd $COLLECTORPATH
    collection_ouput=$(go run main.go collect --interface="${INTERFACE_NAME}" --kubeconfig="${LOCAL_KUBECONFIG}" --output="${DATADIR}/collected.log" --use-analyser-format --duration=${DURATION})
    # log_output=$(go run hack/grab_logs.go -k="${LOCAL_KUBECONFIG}" -o="${DATADIR}" --since="${DURATION}s")
    log_output=$(go run main.go logs -k="${LOCAL_KUBECONFIG}" -o="${DATADIR}" --since="${DURATION}s")
}

analyse_data() {
    cd $ANALYSERPATH/tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/
    dpll_test_result=$(PYTHONPATH=$PPPATH python3 ./testimpl.py $DATADIR/linuxptp-daemon-container-*) # TODO: don't use a wildcard. This breaks if there is more than one file in the directory.
    # echo "${dpll_test_result}"

    cd $ANALYSERPATH
    CONFIGPATH=$ANALYSERPATH/tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/config.yaml
    gnss_test_result=$(PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux ${DATADIR}/collected.log gnss/time-error | PYTHONPATH=$PPPATH python3 -m vse_sync_pp.analyze --canonical --config=$CONFIGPATH - gnss/time-error)
    # echo "${gnss_test_result}"

    echo "Results:"
	echo "DPLL-to-PHC/PRTC-A: $dpll_test_result"
    echo "gnss/time-error: $gnss_test_result"
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
collect_data
analyse_data
