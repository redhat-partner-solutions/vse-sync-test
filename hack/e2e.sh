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
TDPATH=$TESTROOT/testdrive/src
PPPATH=$ANALYSERPATH/src/vse-sync-pp/src

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
TESTJSON="$ARTEFACTDIR/test.json"

ENVJUNIT="$ARTEFACTDIR/env.junit"
TESTJUNIT="$ARTEFACTDIR/test.junit"
FULLJUNIT="$OUTPUTDIR/sync_test_report.xml"

# defaults
DURATION=2000s
NAMESPACE=openshift-ptp
GNSS_NAME=
DIFF_LOG=0

usage() {
    cat - <<EOF
Usage: $(basename "$0") [-i INTERFACE_NAME] [-d DURATION] ?kubeconfig?

Arguments:
    kubeconfig: path to the kubeconfig to be used

Options:
    -i: name of the network interface under test
    -g: name of the gnss device under test
    -d: how many seconds to run data collection

If kubeconfig is not supplied then data collection is skipped:
a pre-existing dataset must be available in $DATADIR

Example usage:
    $(basename "$0") ~/kubeconfig
EOF
}

# Parse arguments and options
while getopts ':i:g:d:l' option; do
    case "$option" in
        i) INTERFACE_NAME="$OPTARG" ;;
	g) GNSS_NAME="$OPTARG" ;;
        d) DURATION="$OPTARG" ;;
	l) DIFF_LOG=1 ;;
        \?) usage >&2 && exit 1 ;;
        :) usage >&2 && exit 1 ;;
    esac

    if [[ -n $INTERFACE_NAME && -n $GNSS_NAME ]]; then
        echo "Only provide one out of interface name or gnss name"
        exit 1
    fi
done
shift $((OPTIND - 1))

LOCAL_KUBECONFIG="$1"

if [ ! -z "$LOCAL_KUBECONFIG" ]; then
    
    CTX=$(oc --kubeconfig=$LOCAL_KUBECONFIG config current-context)
    CLUSTER_UNDER_TEST=$(oc --kubeconfig=$LOCAL_KUBECONFIG config view -ojsonpath="{.contexts[?(@.name == \"$CTX\")].context.cluster}" | sed -e "s/:.*//")
    if [ "$(oc --kubeconfig=$LOCAL_KUBECONFIG get ns $NAMESPACE -o jsonpath='{.status.phase}')" != "Active" ]; then
        echo "$0: error: $NAMESPACE is not active. Check the status of ptp operator namespace." 1>&2
        exit 1
    fi

    oc project --kubeconfig=$LOCAL_KUBECONFIG $NAMESPACE # set namespace for data collection

    if [ -z $INTERFACE_NAME ]; then
        if [[ -z $GNSS_NAME ]]; then
           GNSS_NAME=gnss0
        fi
        INTERFACE_NAME=$(oc --kubeconfig=$LOCAL_KUBECONFIG exec daemonset/linuxptp-daemon -c linuxptp-daemon-container -- ls /sys/class/gnss/${GNSS_NAME}/device/net/)
        echo "Discovered interface name: $INTERFACE_NAME"
    fi
else
    CLUSTER_UNDER_TEST="offline"
fi

mkdir -p $DATADIR
mkdir -p $ARTEFACTDIR
mkdir -p $REPORTARTEFACTDIR
mkdir -p $LOGARTEFACTDIR
mkdir -p $PLOTDIR

pushd "$ANALYSERPATH" >/dev/null 2>&1
SYNCTESTCOMMIT="$(git show -s --format=%H HEAD)"
popd >/dev/null 2>&1

BASEURL_ENV_IDS=https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/
BASEURL_TEST_IDS=https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/
BASEURL_SPECS=https://github.com/redhat-partner-solutions/vse-sync-test/blob/$SYNCTESTCOMMIT/

FINALREPORTPATH=${OUTPUTDIR}"/test_report_"${CLUSTER_UNDER_TEST}"_"$(date -u +'%Y%m%dT%H%M%SZ')"_"$(echo "$SYNCTESTCOMMIT" | head -c 8)".pdf"

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
    "testdrive": $(audit_repo $TDPATH),
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
    go run main.go env verify --interface="$INTERFACE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --use-analyser-format > $ENVJSONRAW
    if [ $? -gt 0 ]
    then
        cat $ENVJSONRAW
    else

        cat $ENVJSONRAW | jq -s -c "$junit_template" > $ENVJSON
    fi
    set -e
    popd >/dev/null 2>&1
}

collect_data(){
    pushd "$COLLECTORPATH" >/dev/null 2>&1

    echo "Collecting $DURATION of data. Please wait..."
    go run main.go collect --interface="$INTERFACE_NAME" --kubeconfig="$LOCAL_KUBECONFIG" --logs-output="$PTP_DAEMON_LOGFILE" --output="$COLLECTED_DATA_FILE" --use-analyser-format --duration=$DURATION
    if [ ${DIFF_LOG} -eq 1 ]
    then
        echo "Collecting $DURATION of data using old method. Please wait..."
        go run hack/logs.go -k="$LOCAL_KUBECONFIG" -o="$LOGARTEFACTDIR/oldmethod.hack" -t="$LOGARTEFACTDIR" -d="$DURATION"
    fi
    rm -r "$LOGARTEFACTDIR" # there are potentially hundreds of MB of logfiles, we keep only the time-window we are interested in.

    popd >/dev/null 2>&1
}

analyse_data() {
    pushd "$ANALYSERPATH" >/dev/null 2>&1

    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $COLLECTED_DATA_FILE 'gnss/time-error' > $GNSS_DEMUXED_PATH
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $COLLECTED_DATA_FILE 'dpll/time-error' > $DPLL_DEMUXED_PATH
    PYTHONPATH=$PPPATH python3 -m vse_sync_pp.demux $COLLECTED_DATA_FILE 'phc/gm-settings' > $PHC_DEMUXED_PATH

    cat <<EOF >> $ARTEFACTDIR/testdrive_config.json
["sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8272/wander-TDEV-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC/PRTC-A/testimpl.py", "$PTP_DAEMON_LOGFILE"]
["sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC/PRTC-B/testimpl.py", "$PTP_DAEMON_LOGFILE"]
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
    env PYTHONPATH=$TDPATH:$PPPATH python3 -m testdrive.run --basedir="$ANALYSERPATH/tests" --imagedir="$PLOTDIR" "$BASEURL_TEST_IDS" $ARTEFACTDIR/testdrive_config.json

    popd >/dev/null 2>&1
}

create_junit() {
    cat $ENVJSON | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit.create --hostname="$CLUSTER_UNDER_TEST" --baseurl-ids="$BASEURL_ENV_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "Environment" - \
        > $ENVJUNIT

    cat $TESTJSON | \
        env PYTHONPATH=$TDPATH python3 -m testdrive.junit.create --hostname="$CLUSTER_UNDER_TEST" --baseurl-ids="$BASEURL_TEST_IDS" --baseurl-specs="$BASEURL_SPECS" --prettify "T-GM Tests" - \
        > $TESTJUNIT

    env PYTHONPATH=$TDPATH python3 -m testdrive.junit.merge --prettify $ARTEFACTDIR/*.junit > $FULLJUNIT
}

create_pdf() {

    pushd "$REPORTGENPATH" >/dev/null 2>&1

    local config=$ARTEFACTDIR/reportgen_config.json
    cat << EOF >> $config
{
    "title": "Synchronization Test Report",
    "subtitle": "T-GM with GNSS",
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
        }
    }
}
EOF

    env PYTHONPATH=$TDPATH make CONFIG=$config JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$(echo "$SYNCTESTCOMMIT" | head -c 8) clean

    if [ -d "$REPORTPRIVSUTGENPATH" ];
    then
        env PYTHONPATH=$TDPATH make CONFIG=$config ATTRIBUTES="allow-uri-read" JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$(echo "$SYNCTESTCOMMIT" | head -c 8) ADOC=$REPORTPRIVSUTGENPATH/doc/setup.adoc PNG=$REPORTPRIVSUTGENPATH/doc/testreport.png all
    else
        env PYTHONPATH=$TDPATH make CONFIG=$config ATTRIBUTES="allow-uri-read" JUNIT=$FULLJUNIT OBJ=$REPORTARTEFACTDIR BUILDER=native GIT_HASH=$(echo "$SYNCTESTCOMMIT" | head -c 8) all
    fi

    mv $REPORTARTEFACTDIR/test-report.pdf $FINALREPORTPATH

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
