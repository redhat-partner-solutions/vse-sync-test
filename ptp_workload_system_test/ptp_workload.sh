#!/bin/bash
#
# PTP Workload - Consumes PTP events, stresses system, validates clock.
#
# Simulates RAN-style workload:
# 1. Continuously reads PTP timestamps (phc_ctl cmp) - consumes PTP
# 2. Runs CPU stress (optional) - stresses system
# 3. Validates clock stays within RAN limit (100 ns) under load
#
# Usage:
#   ./ptp_workload.sh [--duration 300] [--phc-dev /dev/ptp0] [--stress]
#
# Output: JSON to stdout, exit 0=pass, 1=fail

set -e

DURATION=300
PHC_DEV="/dev/ptp0"
STRESS=false
SAMPLE_INTERVAL=0.1
RAN_LIMIT_NS=100

while [[ $# -gt 0 ]]; do
    case $1 in
        --duration) DURATION="$2"; shift 2 ;;
        --phc-dev) PHC_DEV="$2"; shift 2 ;;
        --stress) STRESS=true; shift ;;
        *) shift ;;
    esac
done

max_ns=0
min_ns=999999999
samples=0
start=$(date +%s.%N)
end=$((start + DURATION))

# Background CPU stress
stress_pid=""
if $STRESS && command -v stress-ng &>/dev/null; then
    stress-ng --cpu 2 --timeout ${DURATION}s &
    stress_pid=$!
elif $STRESS; then
    # Simple CPU burn in background
    ( while true; do :; done ) &
    stress_pid=$!
fi

# Main loop: read PTP, record
while true; do
    now=$(date +%s.%N)
    [[ $(echo "$now >= $end" | bc 2>/dev/null || echo 0) -eq 1 ]] && break

    out=$(phc_ctl "$PHC_DEV" cmp 2>&1) || true
    ns=$(echo "$out" | grep -oE "offset[^0-9]*-?[0-9]+[[:space:]]*ns" | grep -oE "-?[0-9]+" | head -1)
    if [[ -n "$ns" ]]; then
        ns=${ns#-}
        samples=$((samples + 1))
        [[ $ns -gt $max_ns ]] && max_ns=$ns
        [[ $ns -lt $min_ns ]] && min_ns=$ns
    fi
    sleep $SAMPLE_INTERVAL
done

# Cleanup stress
[[ -n "$stress_pid" ]] && kill $stress_pid 2>/dev/null || true

elapsed=$(echo "$(date +%s.%N) - $start" | bc 2>/dev/null || echo $DURATION)
pass=false
reason="no samples"
if [[ $samples -gt 0 ]]; then
    if [[ $max_ns -lt $RAN_LIMIT_NS ]]; then
        pass=true
        reason="max time error ${max_ns} ns < limit ${RAN_LIMIT_NS} ns"
    else
        reason="max time error ${max_ns} ns >= limit ${RAN_LIMIT_NS} ns"
    fi
fi

result="pass"
$pass || result="fail"

cat <<EOF
{
  "result": "$result",
  "reason": "$reason",
  "duration": $elapsed,
  "samples": $samples,
  "max_time_error_ns": $max_ns,
  "min_time_error_ns": $min_ns,
  "limit_ns": $RAN_LIMIT_NS
}
EOF

$pass && exit 0 || exit 1
