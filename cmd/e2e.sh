#!/bin/sh

# Start from a directory containing each of the repositories:
# `vse-sync-collection-tools`
# `vse-sync-test`
# `vse-sync-test-report`
# `testdrive`

set -e
set -o pipefail

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
TEST_MODE="gm"  # Options: "gm" (T-GM), "bc" (boundary clock)

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
    go run main.go detect --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --use-analyser-format > $DEVJSON
}


if [ ! -z "$LOCAL_KUBECONFIG" ]; then

    CTX=$(oc --kubeconfig=$LOCAL_KUBECONFIG config current-context)
    CLUSTER_UNDER_TEST=$(oc --kubeconfig=$LOCAL_KUBECONFIG config view -ojsonpath="{.contexts[?(@.name == \"$CTX\")].context.cluster}" | sed -e "s/:.*//")
    if [ "$(oc --kubeconfig=$LOCAL_KUBECONFIG get ns $NAMESPACE -o jsonpath='{.status.phase}')" != "Active" ]; then
        echo "$0: error: $NAMESPACE is not active. Check the status of ptp operator namespace." 1>&2
        exit 1
    fi
    oc project --kubeconfig=$LOCAL_KUBECONFIG $NAMESPACE # set namespace for data collection

    if [ -z $NODE_NAME ]; then
        NUM_OF_NODES=$(oc --kubeconfig=$LOCAL_KUBECONFIG get nodes --output json | jq -j '.items | length')
        if [[ "$NUM_OF_NODES" -gt 1 ]]; then
            echo "nodeName is required for an MNO cluster test run. Please pass in the nodename linked to the interface connected to the GNSS signal"
            exit 1
        fi
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
    local junit_template=$(echo ".[].data + { \"timestamp\": \"$dt\", "duration": 0}")
    set +e
    LOCAL_INTERFACE_NAME=$(jq '.[] | select(.primary == true).name' $DEVJSON)
    go run main.go env verify --interface="$LOCAL_INTERFACE_NAME" --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --use-analyser-format > $ENVJSONRAW

    if [ $? -gt 0 ]
    then
        cat $ENVJSONRAW
    else

        cat $ENVJSONRAW | jq -s -c "$junit_template" > $ENVJSON
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
        if [ $(echo $row |  jq -r .primary) = true ]; then
            echo "Starting main collector for ${LOCAL_INTERFACE_NAME}"
            go run main.go collect --unmanaged-debug-pod --interface="$LOCAL_INTERFACE_NAME" --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --logs-output="$PTP_DAEMON_LOGFILE" --output="$COLLECTED_DATA_FILE" --use-analyser-format --duration=$DURATION  &
            collectorPids+=($!)
        else
            echo "Starting DPLL collector for ${LOCAL_INTERFACE_NAME}"
            go run main.go collect --unmanaged-debug-pod --interface="$LOCAL_INTERFACE_NAME" --nodeName="$NODE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --logs-output="$PTP_DAEMON_LOGFILE" --output="${COLLECTED_DATA_FILE}_${LOCAL_INTERFACE_NAME}" --use-analyser-format --duration=$DURATION --collector="DPLL" &
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
    master_ptp_clock_dev=$(echo $1 |  jq -r .ptp_dev)
    
    # Add G.8272 PHC tests if mode is "gm"
    if [ "$TEST_MODE" = "gm" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
EOF
    fi

    # Add G.8273.2 PHC tests if mode is "bc"
    if [ "$TEST_MODE" = "bc" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/time-error-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8273.2/TDEV-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE", "$master_ptp_clock_dev", $1]
EOF
    fi
}

add_sma1_tests(){
    LOCAL_INTERFACE_NAME=$(echo $1 |  jq -r .name)
    
    # Add G.8272 SMA1 tests if mode is "gm"
    if [ "$TEST_MODE" = "gm" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/time-error-in-locked-mode/DPLL-to-SMA1/PRTC-A/testimpl.py",  "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/time-error-in-locked-mode/DPLL-to-SMA1/PRTC-B/testimpl.py",  "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-SMA1/PRTC-A/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-SMA1/PRTC-B/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-SMA1/PRTC-A/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-SMA1/PRTC-B/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
EOF
    fi

    # Add G.8273.2 SMA1 tests if mode is "bc"
    if [ "$TEST_MODE" = "bc" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/time-error-in-locked-mode/DPLL-to-SMA1/Class-C/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8273.2/TDEV-in-locked-mode/DPLL-to-SMA1/Class-C/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-SMA1/Class-C/testimpl.py", "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}", $1]
EOF
    fi
}


analyse_data() {
    pushd "$ANALYSERPATH" >/dev/null 2>&1

    # Only process GNSS data for T-GM mode (BC doesn't use GNSS constellation tests)
    if [ "$TEST_MODE" = "gm" ]; then
        PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $COLLECTED_DATA_FILE 'gnss/time-error' > $GNSS_DEMUXED_PATH
    fi
    
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $COLLECTED_DATA_FILE 'dpll/time-error' > $DPLL_DEMUXED_PATH
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $COLLECTED_DATA_FILE 'phc/gm-settings' > $PHC_DEMUXED_PATH

    for row in $(jq -c .[] $DEVJSON); do
        if [ $(echo $row |  jq -r .primary) = false ]; then
            LOCAL_INTERFACE_NAME=$(echo $row |  jq -r .name)
            PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux "${COLLECTED_DATA_FILE}_${LOCAL_INTERFACE_NAME}" 'dpll-sma1/time-error' > "${DPLL_DEMUXED_PATH}_${LOCAL_INTERFACE_NAME}"
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
["sync/G.8272/phc/state-transitions/testimpl.py", "$PHC_DEMUXED_PATH"]
EOF
    fi

    # Add G.8273.2 tests if mode is "bc"
    if [ "$TEST_MODE" = "bc" ]; then
        cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8273.2/time-error-in-locked-mode/PHC-to-SYS/RAN/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/time-error-in-locked-mode/1PPS-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/time-error-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/time-error-in-locked-mode/DPLL-to-SMA1/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/TDEV-in-locked-mode/1PPS-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/TDEV-in-locked-mode/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/TDEV-in-locked-mode/DPLL-to-SMA1/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/1PPS-to-DPLL/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-SMA1/Class-C/testimpl.py", "$DPLL_DEMUXED_PATH"]
["sync/G.8273.2/phc/state-transitions/testimpl.py", "$PHC_DEMUXED_PATH"]
EOF
    fi

    for row in $(jq -c .[] $DEVJSON); do
        add_phc_tests $row
        if [ $(echo $row |  jq -r .primary) = false ]; then
            add_sma1_tests $row
        fi
    done

    env PYTHONPATH=$TDPATH:$PPPATH python3 -m testdrive.run --basedir="$ANALYSERPATH/tests" --imagedir="$PLOTDIR" "$BASEURL_TEST_IDS" $ARTEFACTDIR/testdrive_config.json

    popd >/dev/null 2>&1
}

create_junit() {
    cat $ENVJSON | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit.create --hostname="$CLUSTER_UNDER_TEST" --baseurl-ids="$BASEURL_ENV_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "Environment" - \
        > $ENVJUNIT

    # Set test suite name based on test mode
    local test_suite_name
    case "$TEST_MODE" in
        "gm") test_suite_name="T-GM Tests" ;;
        "bc") test_suite_name="T-BC/T-TSC Tests" ;;
    esac

    cat $TESTJSON | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit.create --hostname="$CLUSTER_UNDER_TEST" --baseurl-ids="$BASEURL_TEST_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "$test_suite_name" - \
        > $TESTJUNIT

    env PYTHONPATH=$TDPATH python3 -m testdrive.junit.merge --prettify $ARTEFACTDIR/*.junit > $FULLJUNIT
}

create_pdf() {

    pushd "$REPORTGENPATH" >/dev/null 2>&1

    # Set subtitle based on test mode
    local subtitle
    case "$TEST_MODE" in
        "gm") subtitle="T-GM with GNSS" ;;
        "bc") subtitle="T-BC/T-TSC" ;;
    esac

    local config=$ARTEFACTDIR/reportgen_config.json
    cat << EOF > $config
{
    "title": "Synchronization Test Report",
    "subtitle": "$subtitle",
    "repositories": {
        "vse-sync-test.git": "$ANALYSERPATH/tests/"
    },
    "suites": {
        "Environment": {
            "repository": "vse-sync-test.git",
            "baseurl": "${BASEURL_ENV_IDS}"
        },
        "Synchronization Tests": {
            "repository": "vse-sync-test.git",
            "baseurl": "${BASEURL_TEST_IDS}"
        }
    }
}
EOF

    make CONFIG=$config JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$(echo "$SYNCTESTCOMMIT" | head -c 8) clean

    if [ -d "$REPORTPRIVSUTGENPATH" ];
    then
        make CONFIG=$config ATTRIBUTES="allow-uri-read" JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$(echo "$SYNCTESTCOMMIT" | head -c 8) ADOC=$REPORTPRIVSUTGENPATH/doc/setup.adoc PNG=$REPORTPRIVSUTGENPATH/doc/testreport.png all
    else
        make CONFIG=$config ATTRIBUTES="allow-uri-read" JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$(echo "$SYNCTESTCOMMIT" | head -c 8) all
    fi

    mv $REPORTARTEFACTDIR/test-report.pdf $FINALREPORTPATH

    echo "Generated PDF report: $FINALREPORTPATH"

    popd >/dev/null 2>&1
}

audit_container > $DATADIR/repo_audit
if [ ! -z "$LOCAL_KUBECONFIG" ]; then
    echo "Running Collection"
    verify_env
    collect_data
else
    echo "Skipping data collection"
fi
analyse_data > $TESTJSON
create_junit
create_pdf

# Make exit code indicate test results rather than successful completion.
if grep -Eq '(errors|failures)=\"([^0].*?)\"' $FULLJUNIT; then
    exit 1
else
    exit 0
fi
