# Start in the directory containing the `vse-sync-test` and `vse-sync-testsuite` repositories.

# defaults
DURATION=1000

usage() {
	read -d '' usage_prompt <<- EOF
	Usage: $0 -k KUBECONFIG -i INTERFACE_NAME [-d DURATION]

    Options (required):
        -k: Path to the kubeconfig to be used
        -i: name of the interface to gather data about

    Options (optional):
        -d: How many seconds to run data collection.
    
    Example Usage:
        $0 -k ~/kubeconfig -i ens7f1

	EOF

	echo -e "$usage_prompt"
}

check_required_vars() {
    local required_vars=('LOCAL_KUBECONFIG' 'INTERFACE_NAME')
    local required_vars_err_messages=(
	'KUBECONFIG is invalid or not given. Use the -k option to provide path to one or more kubeconfig files.'
	'INTERFACE_NAME is required. Use the -t option to specify an interface to collect from.'
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

    TESTROOT=$(pwd)
    COLLECTORPATH=$TESTROOT/vse-sync-testsuite
    ANALYSERPATH=$TESTROOT/vse-sync-test
    PPPATH=$ANALYSERPATH/vse-sync-pp/src
    DATADIR=$TESTROOT/data

    mkdir -p $DATADIR
}

collect_data() {
    echo "Collecting $DURATION seconds of data. Please wait..."
    cd $COLLECTORPATH
    collection_ouput=$(go run main.go --interface="${INTERFACE_NAME}" --kubeconfig="${LOCAL_KUBECONFIG}" --output="${DATADIR}/collected.log" --use-analyser-format --count=${DURATION})
    log_output=$(go run hack/grab_logs.go -k="${LOCAL_KUBECONFIG}" -o="${DATADIR}" --since="${DURATION}s")
}

analyse_data() {
    cd $ANALYSERPATH/tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/
    dpll_test_result=$(PYTHONPATH=$PPPATH python3 ./testimpl.py $DATADIR/linuxptp-daemon-container-*)

    cd $ANALYSERPATH
    CONFIGPATH=$ANALYSERPATH/tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/config.yaml
    gnss_test_result=$(PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux ${DATADIR}/collected.log gnss/time-error | PYTHONPATH=$PPPATH python3 -m vse_sync_pp.analyze --canonical --config=$CONFIGPATH - gnss/time-error)
    
    read -d '' results <<- EOF
	Results:

    DPLL-to-PHC/PRTC-A: $dpll_test_result
    gnss/time-error: $gnss_test_result

	EOF

    echo -e "$results"
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
      -*) echo "invalid option: $1" 1>&2; usage_error;;
    esac
done
check_required_vars

collect_data
analyse_data