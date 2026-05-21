#!/bin/sh

# Start from a directory containing each of the repositories:
# `vse-sync-collection-tools`
# `vse-sync-test`
# `vse-sync-test-report`
# `testdrive`

set -e
set -o pipefail

git config --global --add safe.directory /usr/vse/vse-sync-test
git config --global --add safe.directory /usr/vse/vse-sync-collection-tools


TESTROOT=$(pwd)
COLLECTORPATH=$TESTROOT/vse-sync-collection-tools
ANALYSERPATH=$TESTROOT/vse-sync-test
REPORTGENPATH=$TESTROOT/vse-sync-test-report
REPORTPRIVSUTGENPATH=$TESTROOT/vse-sync-sut
TDPATH=$ANALYSERPATH/testdrive/src
PPPATH=$ANALYSERPATH/postprocess/src

OUTPUTDIR=$TESTROOT/data
DATADIR=$OUTPUTDIR/collected # Raw collected data/logs
ARTEFACTDIR=$OUTPUTDIR/artefacts # place mid pipeline files here
PLOTDIR=$ARTEFACTDIR/plots
REPORTARTEFACTDIR=$ARTEFACTDIR/report
LOGARTEFACTDIR=$ARTEFACTDIR/log

COLLECTED_DATA_FILE=$DATADIR/collected.log
PTP_DAEMON_LOGFILE=$DATADIR/linuxptp-daemon-container.log

GNSS_DEMUXED_PATH=$ARTEFACTDIR/gnss-terror.demuxed
DPLL_DEMUXED_PATH=$ARTEFACTDIR/dpll-terror.demuxed
PHC_DEMUXED_PATH=$ARTEFACTDIR/phc-class.demuxed

ENVJSONRAW="$ARTEFACTDIR/env.json.raw"
ENVJSON="$DATADIR/env.json"
DEVJSON="$DATADIR/dev.json"
TESTJSON="$ARTEFACTDIR/test.json"

ENVJUNIT="$ARTEFACTDIR/env.junit"
TESTJUNIT="$ARTEFACTDIR/test.junit"
FULLJUNIT="$OUTPUTDIR/sync_test_report.xml"

# defaults
DURATION=2000s
NAMESPACE=openshift-ptp
NODE_NAME="$PTPNODENAME"
DIFF_LOG=0
TEST_MODE="${PTPTESTMODE:-gm}" # Options: "gm" (T-GM), "bc" (boundary clock)
# Wander MTIE/TDEV plots over 2000s datasets are very slow; skip unless explicitly enabled.
E2E_SKIP_PLOTS="${E2E_SKIP_PLOTS:-1}"
# GNRD: no per-NIC DPLL netlink/sysfs; use linuxptp gnss[]/dpll[] log demux instead.
VSE_DEMUX_DPLL_FROM_LOG="${VSE_DEMUX_DPLL_FROM_LOG:-1}"
# GNRD main collect skips the DPLL collector (netlink probe is slow and always fails).
GNRD_SKIP_DPLL_COLLECTOR="${GNRD_SKIP_DPLL_COLLECTOR:-1}"

usage() {
    cat - <<EOF
Usage: $(basename "$0") [-d DURATION] [-n nodeName] [-m MODE] ?kubeconfig?

Arguments:
    kubeconfig: path to the kubeconfig to be used

Options:
    -d: how many seconds to run data collection
    -n: nodeName that we need to run the tests on (Required for MNO use case)
    -m: test mode - "gm" (T-GM only), "bc" (boundary clock only) (default: gm)

If kubeconfig is not supplied then data collection is skipped:
a pre-existing dataset must be available in $DATADIR

Example usage:
    $(basename "$0") ~/kubeconfig                    # Run T-GM tests (default)
    $(basename "$0") -m gm ~/kubeconfig              # Run T-GM tests only
    $(basename "$0") -m bc ~/kubeconfig              # Run boundary clock tests only
EOF
}

# Parse arguments and options
while getopts ':d:l:n:m:' option; do
    case "$option" in
    d) DURATION="$OPTARG" ;;
    l) DIFF_LOG=1 ;;
    n) NODE_NAME="$OPTARG" ;;
    m) TEST_MODE="$OPTARG" ;;
    \?) usage >&2 && exit 1 ;;
    :) usage >&2 && exit 1 ;;
    esac
done

# Validate test mode
case "$TEST_MODE" in
    "gm"|"bc") ;;
    *) echo "Error: Invalid test mode '$TEST_MODE'. Must be 'gm' or 'bc'." >&2 && usage >&2 && exit 1 ;;
esac
shift $((OPTIND - 1))

LOCAL_KUBECONFIG="$1"

if [ ! -z $NODE_NAME ]; then
    echo "Using node name ${NODE_NAME}"
fi

echo "Test mode: $TEST_MODE"
case "$TEST_MODE" in
    "gm") echo "  Running T-GM tests only (G.8272)" ;;
    "bc") echo "  Running boundary clock tests only (G.8273.2)" ;;
esac

detect_configured_cards() {
    pushd "$COLLECTORPATH" >/dev/null 2>&1
    echo "Detecting cards configured in ptpconfig. Please wait..."
    go run main.go detect --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --use-analyser-format --clock-type="$TEST_MODE" > "$DEVJSON" 2>"$DATADIR/detect.log"
}


if [ ! -z "$LOCAL_KUBECONFIG" ]; then

    CTX=$(oc --kubeconfig=$LOCAL_KUBECONFIG config current-context)
    CLUSTER_UNDER_TEST=$(oc --kubeconfig=$LOCAL_KUBECONFIG config view -ojsonpath="{.contexts[?(@.name == \"$CTX\")].context.cluster}" | sed -e "s/:.*//")
    if [ "$(oc --kubeconfig=$LOCAL_KUBECONFIG get ns $NAMESPACE -o jsonpath='{.status.phase}')" != "Active" ]; then
        echo "$0: error: $NAMESPACE is not active. Check the status of ptp operator namespace." 1>&2
        exit 1
    fi
    oc project --kubeconfig=$LOCAL_KUBECONFIG $NAMESPACE # set namespace for data collection

    if [ -z "$NODE_NAME" ]; then
        NUM_OF_NODES=$(oc --kubeconfig=$LOCAL_KUBECONFIG get nodes --output json | jq -j '.items | length')
        if [ "$NUM_OF_NODES" -gt 1 ]; then
            echo "nodeName is required for an MNO cluster test run. Please pass in the nodename linked to the interface connected to the GNSS signal" 1>&2
            exit 1
        fi
        NODE_NAME=$(oc --kubeconfig=$LOCAL_KUBECONFIG get nodes -o jsonpath='{.items[0].metadata.name}')
        echo "Using node name ${NODE_NAME} (single-node cluster)"
    fi
else
    CLUSTER_UNDER_TEST="offline"
fi

mkdir -p $DATADIR
mkdir -p $ARTEFACTDIR
mkdir -p $REPORTARTEFACTDIR
mkdir -p $LOGARTEFACTDIR
mkdir -p $PLOTDIR

if [ "$CLUSTER_UNDER_TEST" != "offline" ]; then
    detect_configured_cards
fi

pushd "$ANALYSERPATH" >/dev/null 2>&1
SYNCTESTCOMMIT="$(git show -s --format=%H HEAD)"
popd >/dev/null 2>&1

BASEURL_ENV_IDS=https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/
BASEURL_TEST_IDS=https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/
BASEURL_SPECS=https://github.com/redhat-partner-solutions/vse-sync-test/blob/$SYNCTESTCOMMIT/

# Set report filename suffix based on test mode
case "$TEST_MODE" in
    "gm") MODE_SUFFIX="_TGM" ;;
    "bc") MODE_SUFFIX="_TBC_TSC" ;;
esac

FINALREPORTPATH=${OUTPUTDIR}"/test_report"${MODE_SUFFIX}"_"${CLUSTER_UNDER_TEST}"_"$(date -u +'%Y%m%dT%H%M%SZ')"_"$(echo "$SYNCTESTCOMMIT" | head -c 8)".pdf"

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
    "vse-sync-test-report": $(audit_repo $REPORTGENPATH)
}
EOF
}


verify_env(){
    pushd "$COLLECTORPATH" >/dev/null 2>&1

    echo "Verifying test env. Please wait..."
    dt=$(date --rfc-3339='seconds' -u)
    local junit_template
    junit_template=$(printf '.[].data + {"timestamp": "%s", "duration": 0}' "$dt")
    set +e
    LOCAL_INTERFACE_NAME=$(jq -r '.[] | select(.primary == true) | .name' "$DEVJSON")
    if [ -z "$LOCAL_INTERFACE_NAME" ]; then
        echo "$0: error: no primary interface in $DEVJSON" 1>&2
        cat "$DEVJSON" 1>&2
        exit 1
    fi
    go run main.go env verify --interface="$LOCAL_INTERFACE_NAME" --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --use-analyser-format --clock-type="$TEST_MODE" > "$ENVJSONRAW" 2>"$ARTEFACTDIR/env-verify.log"

    if [ $? -gt 0 ]
    then
        cat $ENVJSONRAW
    else

        grep -E '^\{"data":\{"analysis"' "$ENVJSONRAW" | jq -s -c "$junit_template" > $ENVJSON
    fi
    set -e
    popd >/dev/null 2>&1
}

run_collector(){
    echo "Running main collector for $1"
    return $!
}

run_just_dpll_collector(){
    echo "Running dpll collector for $1"
    return $!
}

collect_data(){
    pushd "$COLLECTORPATH" >/dev/null 2>&1
    go run main.go start-debug --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG"

    echo "Collecting $DURATION of data. Please wait..."
    DATE_DURATION=$(echo $DURATION | sed 's|\([0-9][0-9]*\)s|\1 seconds|g' | sed 's|\([0-9][0-9]*\)m|\1 minutes|g'| sed 's|\([0-9][0-9]*\)d|\1 days|g')
    END_DATE=$(date --date="+$DATE_DURATION" +"%Y-%m-%d %H:%M %Z")
    echo "expected end: $END_DATE"

    declare -a collectorPids=()
    for row in $(jq -c .[] $DEVJSON); do
        LOCAL_INTERFACE_NAME=$(echo $row |  jq -r .name)
        if [ "$(echo "$row" | jq -r .primary)" = true ]; then
            echo "Starting main collector for ${LOCAL_INTERFACE_NAME}"
            collect_args="--unmanaged-debug-pod --interface=${LOCAL_INTERFACE_NAME} --nodeName=${NODE_NAME} --kubeconfig=${LOCAL_KUBECONFIG} --logs-output=${PTP_DAEMON_LOGFILE} --output=${COLLECTED_DATA_FILE} --use-analyser-format --duration=${DURATION} --clock-type=${TEST_MODE}"
            if [ "$GNRD_SKIP_DPLL_COLLECTOR" = "1" ]; then
                # GNRD: GNSS + PMC + logs only; DPLL samples come from dpll[] log demux.
                collect_args="${collect_args} --collector=GNSS --collector=PMC --collector=Logs"
            fi
            # shellcheck disable=SC2086
            go run main.go collect ${collect_args} &
            collectorPids+=($!)
        elif [ "$VSE_DEMUX_DPLL_FROM_LOG" = "1" ]; then
            echo "Skipping DPLL collector for ${LOCAL_INTERFACE_NAME} (linuxptp log demux)"
        else
            echo "Starting DPLL collector for ${LOCAL_INTERFACE_NAME}"
            go run main.go collect --unmanaged-debug-pod --interface="$LOCAL_INTERFACE_NAME" --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --logs-output="$PTP_DAEMON_LOGFILE" --output="${COLLECTED_DATA_FILE}_${LOCAL_INTERFACE_NAME}" --use-analyser-format --duration=$DURATION --clock-type="$TEST_MODE" --collector="DPLL" &
            collectorPids+=($!)
        fi
    done

    echo "Waiting on collectors ${collectorPids[@]}"
    wait -f "${collectorPids[@]}"

    go run main.go stop-debug --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG"

    if [ ${DIFF_LOG} -eq 1 ]
    then
        echo "Collecting $DURATION of data using old method. Please wait..."
        go run hack/logs.go -k="$LOCAL_KUBECONFIG" -o="$LOGARTEFACTDIR/oldmethod.hack" -t="$LOGARTEFACTDIR" -d="$DURATION"
    fi
    rm -r "$LOGARTEFACTDIR" # there are potentially hundreds of MB of logfiles, we keep only the time-window we are interested in.

    popd >/dev/null 2>&1
}


add_phc_tests() {
    local_interface_name=$(echo "$1" | jq -r .name)
    phc_log_file="$ARTEFACTDIR/ts2phc_${local_interface_name}.log"
    if [ ! -s "$phc_log_file" ]; then
        echo "Skipping DPLL-to-PHC tests for ${local_interface_name} (no ts2phc/dpll log lines)" >&2
        return
    fi

    # Add G.8272 PHC tests if mode is "gm"
    if [ "$TEST_MODE" = "gm" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
EOF
    fi

    # Add G.8273.2 PHC tests if mode is "bc"
    if [ "$TEST_MODE" = "bc" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/time-error-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8273.2/TDEV-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C/testimpl.py", "$phc_log_file", "$local_interface_name", $1]
EOF
    fi
}

add_sma1_tests(){
    LOCAL_INTERFACE_NAME=$(echo "$1" | jq -r .name)
    sma1_demux="${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}"
    if [ ! -s "$sma1_demux" ]; then
        echo "Skipping SMA1-to-DPLL tests for ${LOCAL_INTERFACE_NAME} (no dpll log data for this interface on GNRD)" >&2
        return
    fi

    # Add G.8272 SMA1 tests if mode is "gm"
    if [ "$TEST_MODE" = "gm" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/time-error-in-locked-mode/SMA1-to-DPLL/PRTC-A/testimpl.py",  "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/time-error-in-locked-mode/SMA1-to-DPLL/PRTC-B/testimpl.py",  "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/SMA1-to-DPLL/PRTC-A/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/SMA1-to-DPLL/PRTC-B/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/SMA1-to-DPLL/PRTC-A/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/SMA1-to-DPLL/PRTC-B/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
EOF
    fi

    # Add G.8273.2 SMA1 tests if mode is "bc"
    if [ "$TEST_MODE" = "bc" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/time-error-in-locked-mode/SMA1-to-DPLL/Class-C/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8273.2/TDEV-in-locked-mode/SMA1-to-DPLL/Class-C/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/SMA1-to-DPLL/Class-C/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
EOF
    fi
}


# Grep linuxptp log down to relevant lines before Python parse (full daemon logs are 80k+ lines).
log_grep_pattern() {
    parser_id="$1"
    interface_name="$2"
    case "$parser_id" in
        gnss/time-error) echo '^gnss\[' ;;
        dpll/time-error|dpll-sma1/time-error)
            if [ -n "$interface_name" ]; then
                printf '^dpll\\[[0-9]+\\]:.*[[:space:]]%s[[:space:]]' "$interface_name"
            else
                echo '^dpll\['
            fi
            ;;
        *) echo '.' ;;
    esac
}

parse_ptp_log_to_file() {
    parser_id="$1"
    outfile="$2"
    interface_name="$3"
    if [ ! -f "$PTP_DAEMON_LOGFILE" ]; then
        return 1
    fi
    pattern=$(log_grep_pattern "$parser_id" "$interface_name")
    tmp=$(mktemp "${outfile}.XXXXXX")
    grep -E "$pattern" "$PTP_DAEMON_LOGFILE" >"$tmp" 2>/dev/null || true
    if [ ! -s "$tmp" ]; then
        rm -f "$tmp"
        return 1
    fi
    if [ -n "$interface_name" ] && [ "$parser_id" != "gnss/time-error" ]; then
        PYTHONPATH=$PPPATH python3 -m vse_sync_pp.parse --interface="$interface_name" "$tmp" "$parser_id" >"$outfile"
    else
        PYTHONPATH=$PPPATH python3 -m vse_sync_pp.parse "$tmp" "$parser_id" >"$outfile"
    fi
    rm -f "$tmp"
}

# GNRD: prefer linuxptp operator log lines (collector DPLL/netlink is unavailable).
demux_or_parse_from_log() {
    parser_id="$1"
    outfile="$2"
    collect_file="${3:-$COLLECTED_DATA_FILE}"
    if [ "$VSE_DEMUX_DPLL_FROM_LOG" = "1" ] && [ "$parser_id" != "phc/gm-settings" ]; then
        parse_ptp_log_to_file "$parser_id" "$outfile" "" || true
        return
    fi
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux "$collect_file" "$parser_id" >"$outfile" 2>/dev/null || true
    if [ ! -s "$outfile" ]; then
        parse_ptp_log_to_file "$parser_id" "$outfile" "" || true
    fi
}

demux_or_parse_dpll_from_log() {
    parser_id="$1"
    outfile="$2"
    interface_name="$3"
    collect_file="${4:-$COLLECTED_DATA_FILE}"
    if [ "$VSE_DEMUX_DPLL_FROM_LOG" = "1" ]; then
        parse_ptp_log_to_file "$parser_id" "$outfile" "$interface_name" || true
        return
    fi
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux "$collect_file" "$parser_id" >"$outfile" 2>/dev/null || true
    if [ ! -s "$outfile" ]; then
        parse_ptp_log_to_file "$parser_id" "$outfile" "$interface_name" || true
    fi
}

# Filtered ts2phc/dpll log per netdev (avoids scanning 80k+ line daemon logs in each test).
prepare_ts2phc_log_for_interface() {
    interface_name="$1"
    outfile="$ARTEFACTDIR/ts2phc_${interface_name}.log"
    if [ ! -f "$PTP_DAEMON_LOGFILE" ]; then
        return 1
    fi
    grep -E "^ts2phc\\[[0-9]+(\\.[0-9]+)?\\]:.*[[:space:]]${interface_name}[[:space:]]" \
        "$PTP_DAEMON_LOGFILE" >"$outfile" 2>/dev/null || true
    if [ ! -s "$outfile" ]; then
        grep -E "^dpll\\[[0-9]+\\]:.*[[:space:]]${interface_name}[[:space:]]" \
            "$PTP_DAEMON_LOGFILE" >>"$outfile" 2>/dev/null || true
    fi
    [ -s "$outfile" ]
}

analyse_data() {
    echo "Analysing collected data. Please wait..." >&2
    pushd "$ANALYSERPATH" >/dev/null 2>&1

    # Get primary interface name for PTP4L tests
    PRIMARY_INTERFACE_NAME=$(jq -r '.[] | select(.primary == true).name' $DEVJSON)

    # Only process GNSS data for T-GM mode (BC doesn't use GNSS constellation tests)
    if [ "$TEST_MODE" = "gm" ]; then
        demux_or_parse_from_log 'gnss/time-error' "$GNSS_DEMUXED_PATH"
    fi

    demux_or_parse_from_log 'dpll/time-error' "$DPLL_DEMUXED_PATH"
    demux_or_parse_from_log 'phc/gm-settings' "$PHC_DEMUXED_PATH"

    for row in $(jq -c .[] $DEVJSON); do
        if [ $(echo $row |  jq -r .primary) = false ]; then
            LOCAL_INTERFACE_NAME=$(echo $row |  jq -r .name)
            demux_or_parse_dpll_from_log 'dpll-sma1/time-error' \
                "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}" \
                "$LOCAL_INTERFACE_NAME" \
                "${COLLECTED_DATA_FILE}_${LOCAL_INTERFACE_NAME}"
        fi
    done

    # Create test configuration based on selected mode
    cat <<EOF > $ARTEFACTDIR/testdrive_config.json
EOF

    # Add G.8272 tests if mode is "gm"
    if [ "$TEST_MODE" = "gm" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/time-error-in-locked-mode/PHC-to-SYS/RAN/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/testimpl.py", "$GNSS_DEMUXED_PATH"]
["sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/testimpl.py", "$GNSS_DEMUXED_PATH"]
["sync/G.8272/wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/testimpl.py", "$GNSS_DEMUXED_PATH"]
["sync/G.8272/wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/testimpl.py", "$GNSS_DEMUXED_PATH"]
["sync/G.8272/wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/testimpl.py", "$GNSS_DEMUXED_PATH"]
["sync/G.8272/wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/testimpl.py", "$GNSS_DEMUXED_PATH"]
["sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-A/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-B/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8272/wander-TDEV-in-locked-mode/1PPS-to-DPLL/PRTC-A/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8272/wander-TDEV-in-locked-mode/1PPS-to-DPLL/PRTC-B/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8272/wander-MTIE-in-locked-mode/1PPS-to-DPLL/PRTC-A/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8272/wander-MTIE-in-locked-mode/1PPS-to-DPLL/PRTC-B/testimpl.py", "$DPLL_DEMUXED_PATH"]
EOF
        if [ -s "$PHC_DEMUXED_PATH" ]; then
            cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/phc/state-transitions/testimpl.py", "$PHC_DEMUXED_PATH"]
EOF
        else
            echo "Skipping phc/state-transitions (no PMC gm-settings data collected)" >&2
        fi
    fi

    # Add G.8273.2 tests if mode is "bc"
    if [ "$TEST_MODE" = "bc" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/time-error-in-locked-mode/PHC-to-SYS/RAN/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/time-error-in-locked-mode/1PPS-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/time-error-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/time-error-in-locked-mode/SMA1-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/time-error-in-locked-mode/PTP4L-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/TDEV-in-locked-mode/1PPS-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/TDEV-in-locked-mode/SMA1-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/TDEV-in-locked-mode/PTP4L-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/1PPS-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/SMA1-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/PTP4L-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
EOF
        if [ -s "$PHC_DEMUXED_PATH" ]; then
            cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/phc/state-transitions/testimpl.py", "$PHC_DEMUXED_PATH"]
EOF
        else
            echo "Skipping phc/state-transitions (no PMC gm-settings data collected)" >&2
        fi
    fi

    for row in $(jq -c .[] "$DEVJSON"); do
        iface_name=$(echo "$row" | jq -r .name)
        if [ -n "$iface_name" ]; then
            prepare_ts2phc_log_for_interface "$iface_name" || true
        fi
        if [ "$(echo "$row" | jq -r .primary)" = true ]; then
            add_phc_tests "$row"
        elif [ "$(echo "$row" | jq -r .primary)" = false ]; then
            add_sma1_tests "$row"
        fi
    done

    if [ ! -s "$GNSS_DEMUXED_PATH" ] && [ "$TEST_MODE" = "gm" ]; then
        echo "warning: no GNSS time-error samples demuxed (check linuxptp gnss[] log lines)" 1>&2
    fi
    if [ ! -s "$DPLL_DEMUXED_PATH" ]; then
        echo "warning: no DPLL time-error samples demuxed (check linuxptp dpll[] log lines)" 1>&2
    fi

    echo "Running sync tests. Please wait..." >&2
    if [ "$E2E_SKIP_PLOTS" = "1" ]; then
        env PYTHONPATH=$TDPATH:$PPPATH python3 -m testdrive.run \
            --basedir="$ANALYSERPATH/tests" "$BASEURL_TEST_IDS" $ARTEFACTDIR/testdrive_config.json
    else
        env PYTHONPATH=$TDPATH:$PPPATH python3 -m testdrive.run \
            --basedir="$ANALYSERPATH/tests" --imagedir="$PLOTDIR" "$BASEURL_TEST_IDS" $ARTEFACTDIR/testdrive_config.json
    fi

    popd >/dev/null 2>&1
}

create_junit() {
    echo "Creating JUnit report. Please wait..."
    if [ -s "$ENVJSON" ]; then
        cat "$ENVJSON" | \
            env PYTHONPATH=$TDPATH python3 -m testdrive.junit.create --hostname="$CLUSTER_UNDER_TEST" --baseurl-ids="$BASEURL_ENV_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "Environment" - \
            > "$ENVJUNIT"
    else
        echo "warning: empty env.json; skipping Environment JUnit section" 1>&2
        : > "$ENVJUNIT"
    fi

    # Set test suite name based on test mode
    local test_suite_name
    case "$TEST_MODE" in
        "gm") test_suite_name="T-GM Tests" ;;
        "bc") test_suite_name="T-BC/T-TSC Tests" ;;
    esac

    if [ ! -s "$TESTJSON" ]; then
        echo "$0: error: test analysis produced no output at $TESTJSON" 1>&2
        exit 1
    fi
    cat "$TESTJSON" | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit.create --hostname="$CLUSTER_UNDER_TEST" --baseurl-ids="$BASEURL_TEST_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "$test_suite_name" - \
        > "$TESTJUNIT"

    junit_files=""
    for f in "$ENVJUNIT" "$TESTJUNIT"; do
        if [ -s "$f" ]; then
            junit_files="$junit_files $f"
        fi
    done
    if [ -z "$junit_files" ]; then
        echo "$0: error: no JUnit files to merge" 1>&2
        exit 1
    fi
    # shellcheck disable=SC2086
    env PYTHONPATH=$TDPATH python3 -m testdrive.junit.merge --prettify $junit_files > "$FULLJUNIT"
}

create_pdf() {
    echo "Generating PDF report. Please wait..."

    pushd "$REPORTGENPATH" >/dev/null 2>&1

    # Set subtitle based on test mode
    local subtitle
    case "$TEST_MODE" in
        "gm") subtitle="T-GM with GNSS" ;;
        "bc") subtitle="T-BC/T-TSC" ;;
    esac

    local config=$ARTEFACTDIR/reportgen_config.json
    local git_hash
    git_hash=$(echo "$SYNCTESTCOMMIT" | head -c 8)
    # Suite keys must match junit testcase classname (see create_junit test_suite_name).
    cat << EOF > $config
{
    "title": "Synchronization Test Report",
    "subtitle": "$subtitle",
    "githash": "$git_hash",
    "repositories": {
        "vse-sync-test.git": "$ANALYSERPATH/tests/"
    },
    "suites": {
        "Environment": {
            "repository": "vse-sync-test.git",
            "baseurl": "${BASEURL_ENV_IDS}"
        },
        "T-GM Tests": {
            "repository": "vse-sync-test.git",
            "baseurl": "${BASEURL_TEST_IDS}"
        },
        "T-BC/T-TSC Tests": {
            "repository": "vse-sync-test.git",
            "baseurl": "${BASEURL_TEST_IDS}"
        }
    }
}
EOF

    if [ ! -s "$FULLJUNIT" ]; then
        echo "$0: error: $FULLJUNIT is missing or empty; cannot build PDF" 1>&2
        exit 1
    fi

    make CONFIG="$config" JUNIT="$FULLJUNIT" OBJ="$REPORTARTEFACTDIR" BUILDER=native "GIT_HASH=$git_hash" clean

    pdf_make_args="CONFIG=$config ATTRIBUTES=allow-uri-read JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$git_hash"
    if [ -d "$REPORTPRIVSUTGENPATH" ];
    then
        # shellcheck disable=SC2086
        timeout 600 make $pdf_make_args ADOC=$REPORTPRIVSUTGENPATH/doc/setup.adoc PNG=$REPORTPRIVSUTGENPATH/doc/testreport.png all \
            || { echo "PDF generation timed out after 600s" >&2; exit 1; }
    else
        # shellcheck disable=SC2086
        timeout 600 make $pdf_make_args all \
            || { echo "PDF generation timed out after 600s" >&2; exit 1; }
    fi

    if [ ! -f "$REPORTARTEFACTDIR/test-report.pdf" ]; then
        echo "$0: error: PDF build did not produce $REPORTARTEFACTDIR/test-report.pdf" 1>&2
        exit 1
    fi
    mv "$REPORTARTEFACTDIR/test-report.pdf" "$FINALREPORTPATH"

    echo "Generated PDF report: $FINALREPORTPATH"

    popd >/dev/null 2>&1
}

# PDF is always produced when analysis completes; exit status reflects pass/fail of tests only.
report_exit_code() {
    if grep -Eq '(errors|failures)=\"([^0].*?)\"' "$FULLJUNIT"; then
        return 1
    fi
    return 0
}

audit_container > $DATADIR/repo_audit
if [ ! -z "$LOCAL_KUBECONFIG" ]; then
    echo "Running Collection"
    verify_env
    collect_data
    echo "Collection finished."
else
    echo "Skipping data collection"
fi
analyse_data > $TESTJSON
echo "Analysis finished." >&2
create_junit
create_pdf

# Exit 1 when tests failed, 0 when all passed (PDF is already written).
if report_exit_code; then
    exit 0
else
    echo "Some tests failed; see $FULLJUNIT and $FINALREPORTPATH" 1>&2
    exit 1
fi
