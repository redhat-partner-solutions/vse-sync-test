#!/usr/bin/env python3
"""
PTP Workload - Consumes PTP events, stresses system, validates clock.

This workload simulates a RAN-style consumer that:
1. Continuously reads PTP timestamps (PHC) - consuming PTP events
2. Runs CPU/stress load to stress the system
3. Records clock accuracy during the workload
4. Validates clock meets RAN requirements (< 100 ns time error) under load

Usage:
  Run inside linuxptp-daemon container or on host with PHC access:
  python3 ptp_workload.py --duration 300 --phc-dev /dev/ptp0 [--stress-cpu]

Output: JSON with result, max_time_error_ns, samples, pass/fail
"""

import argparse
import json
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional

# RAN workload requirement: 100 ns max time error
RAN_TIME_ERROR_LIMIT_NS = 100


@dataclass
class WorkloadResult:
    """Result of PTP workload test."""
    pass_: bool = False
    result: str = "error"
    reason: str = ""
    duration_s: float = 0.0
    samples: int = 0
    max_time_error_ns: int = 0
    min_time_error_ns: int = 0
    stress_errors: int = 0


def read_phc_cmp(phc_dev: str) -> Optional[int]:
    """Read PHC vs CLOCK_REALTIME offset using phc_ctl cmp. Returns offset in ns or None."""
    # Try phc_ctl from PATH, then common locations (containers may have it in /usr/sbin)
    for cmd in (["phc_ctl", phc_dev, "cmp"], ["/usr/sbin/phc_ctl", phc_dev, "cmp"]):
        try:
            out = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )
            text = out.stdout + out.stderr
            # Multiple patterns for different phc_ctl output formats
            for pattern in (
                r"offset\s+(?:from\s+CLOCK_REALTIME\s+is\s+)?(-?\d+)\s*ns",  # "offset from CLOCK_REALTIME is -37001639797ns"
                r"offset\s+is\s+(-?\d+)\s*ns",  # "offset is 123 ns"
                r"offset[^0-9]*(-?\d+)\s*ns",   # permissive
                r"(-?\d+)\s*ns\s*(?:offset|$)", # "123 ns" near offset
            ):
                match = re.search(pattern, text, re.I)
                if match:
                    return abs(int(match.group(1)))
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue
    return None


def stress_worker(stop_event: threading.Event, cpu_load: float = 0.5) -> None:
    """Background CPU stress - consumes CPU to simulate workload."""
    while not stop_event.is_set():
        # Simple CPU burn
        start = time.perf_counter()
        while time.perf_counter() - start < 0.1 and not stop_event.is_set():
            _ = sum(range(10000))


def run_workload(
    duration_s: int,
    phc_dev: str = "/dev/ptp0",
    stress_cpu: bool = True,
    sample_interval_s: float = 0.1,
) -> WorkloadResult:
    """Run PTP workload: consume PTP, stress system, validate clock."""
    result = WorkloadResult()
    result.duration_s = duration_s

    samples: List[int] = []
    stop_event = threading.Event()

    # Start stress thread
    if stress_cpu:
        stress_thread = threading.Thread(target=stress_worker, args=(stop_event,))
        stress_thread.start()

    # Main loop: read PTP timestamps, record errors
    end_time = time.time() + duration_s
    last_sample = 0.0

    while time.time() < end_time:
        now = time.time()
        if now - last_sample >= sample_interval_s:
            offset_ns = read_phc_cmp(phc_dev)
            if offset_ns is not None:
                samples.append(offset_ns)
            last_sample = now
        time.sleep(0.01)

    stop_event.set()
    if stress_cpu:
        stress_thread.join(timeout=2)

    result.samples = len(samples)
    if not samples:
        result.result = "error"
        result.reason = (
            "no PTP samples collected - check phc_ctl in PATH, PHC device access, "
            "and phc_ctl cmp output format"
        )
        return result

    result.max_time_error_ns = max(samples)
    result.min_time_error_ns = min(samples)
    result.pass_ = result.max_time_error_ns < RAN_TIME_ERROR_LIMIT_NS
    result.result = "pass" if result.pass_ else "fail"
    result.reason = (
        f"max time error {result.max_time_error_ns} ns "
        f"{'<' if result.pass_ else '>='} limit {RAN_TIME_ERROR_LIMIT_NS} ns"
    )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="PTP workload: consume events, stress, validate clock")
    parser.add_argument("--duration", type=int, default=300, help="Workload duration in seconds")
    parser.add_argument("--phc-dev", default="/dev/ptp0", help="PHC device path")
    parser.add_argument("--stress-cpu", action="store_true", default=True, help="Enable CPU stress")
    parser.add_argument("--no-stress", action="store_true", help="Disable CPU stress")
    parser.add_argument("--sample-interval", type=float, default=0.1, help="Sample interval in seconds")
    args = parser.parse_args()

    result = run_workload(
        duration_s=args.duration,
        phc_dev=args.phc_dev,
        stress_cpu=args.stress_cpu and not args.no_stress,
        sample_interval_s=args.sample_interval,
    )

    output = {
        "result": result.result,
        "reason": result.reason,
        "duration": result.duration_s,
        "samples": result.samples,
        "max_time_error_ns": result.max_time_error_ns,
        "min_time_error_ns": result.min_time_error_ns,
        "limit_ns": RAN_TIME_ERROR_LIMIT_NS,
    }
    print(json.dumps(output, indent=2))
    return 0 if result.pass_ else 1


if __name__ == "__main__":
    sys.exit(main())
