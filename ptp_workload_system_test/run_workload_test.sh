#!/bin/bash
#
# Run PTP Workload System Test
#
# Executes the PTP workload inside the linuxptp-daemon pod.
# Requires: oc/kubectl, KUBECONFIG, PTP namespace with linuxptp-daemon
#
# Usage:
#   ./run_workload_test.sh [kubeconfig] [duration]
#
# Example:
#   KUBECONFIG=/path/to/kubeconfig ./run_workload_test.sh
#   ./run_workload_test.sh /path/to/kubeconfig 600

KUBECONFIG="${1:-${KUBECONFIG}}"
DURATION="${2:-300}"
NAMESPACE="${PTP_NAMESPACE:-openshift-ptp}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[[ -z "$KUBECONFIG" ]] && { echo "KUBECONFIG required"; exit 1; }
[[ ! -f "$KUBECONFIG" ]] && { echo "KUBECONFIG not found: $KUBECONFIG"; exit 1; }

POD=$(oc --kubeconfig="$KUBECONFIG" get pods -n "$NAMESPACE" -l app=linuxptp-daemon -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
[[ -z "$POD" ]] && { echo "linuxptp-daemon pod not found"; exit 1; }

# Get first PHC device (container may be linuxptp-daemon or ptp)
CONTAINER=$(oc --kubeconfig="$KUBECONFIG" get pod -n "$NAMESPACE" "$POD" -o jsonpath='{.spec.containers[0].name}' 2>/dev/null || echo "linuxptp-daemon")
PHC_DEV=$(oc --kubeconfig="$KUBECONFIG" exec -n "$NAMESPACE" "$POD" -c "$CONTAINER" -- ls /dev/ptp* 2>/dev/null | head -1 || echo "/dev/ptp0")

echo "Running PTP workload for ${DURATION}s on $POD (PHC: $PHC_DEV)" >&2

# Copy ptp_workload.py to pod and run, or run inline Python
if oc --kubeconfig="$KUBECONFIG" cp "$SCRIPT_DIR/ptp_workload.py" "$NAMESPACE/$POD:/tmp/ptp_workload.py" -c "$CONTAINER" 2>/dev/null; then
    oc --kubeconfig="$KUBECONFIG" exec -n "$NAMESPACE" "$POD" -c "$CONTAINER" -- \
        python3 /tmp/ptp_workload.py --duration "$DURATION" --phc-dev "$PHC_DEV" --stress-cpu
else
    # Fallback: inline minimal workload (no Python/copy needed)
    # Try phc_ctl from PATH or /usr/sbin; parse offset with flexible grep
    oc --kubeconfig="$KUBECONFIG" exec -n "$NAMESPACE" "$POD" -c "$CONTAINER" -- \
        sh -c "PHC_CMD=\$(command -v phc_ctl 2>/dev/null || echo /usr/sbin/phc_ctl);
        D=$DURATION; P=$PHC_DEV; L=100; max=0; samples=0; start=\$(date +%s);
        while [ \$(date +%s) -lt \$((start + D)) ]; do
            raw=\$(\$PHC_CMD \$P cmp 2>&1);
            ns=\$(echo \"\$raw\" | grep -oE 'offset[^0-9]*-?[0-9]+' | grep -oE '-?[0-9]+' | head -1);
            ns=\${ns#-};
            [ -n \"\$ns\" ] && { samples=\$((samples+1)); [ \$ns -gt \$max ] && max=\$ns; };
            sleep 0.1;
        done;
        [ \$max -lt \$L ] && r=pass || r=fail;
        echo \"{\\\"result\\\":\\\"\$r\\\",\\\"reason\\\":\\\"samples \\\$samples max_ns \\\$max limit \\\$L ns\\\",\\\"max_time_error_ns\\\":\$max,\\\"samples\\\":\$samples,\\\"limit_ns\\\":\$L,\\\"duration\\\":\$D}\";
        [ \"\$r\" = pass ]"
fi
