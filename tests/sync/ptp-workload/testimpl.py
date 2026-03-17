#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""PTP Workload System Test - Consumes PTP events, stresses system, validates clock.

Reads the workload result file produced by run_workload_test.sh during e2e.
Outputs testdrive-compatible JSON for inclusion in the PDF report.
"""

import json
import sys
from argparse import ArgumentParser
from os.path import exists

from vse_sync_pp.common import print_loj


def refimpl(result_file: str):
    """Read workload result and return testdrive-compatible dict."""
    if not exists(result_file):
        return {
            "result": False,
            "reason": "PTP workload not run (offline mode or workload failed before output)",
            "analysis": {"skipped": True},
        }
    try:
        with open(result_file, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return {
            "result": False,
            "reason": f"Failed to read workload result: {e}",
            "analysis": {},
        }
    passed = data.get("result") == "pass"
    reason = data.get("reason", "unknown")
    return {
        "result": passed,
        "reason": reason,
        "analysis": {
            "max_time_error_ns": data.get("max_time_error_ns"),
            "samples": data.get("samples"),
            "limit_ns": data.get("limit_ns"),
            "duration": data.get("duration"),
        },
    }


def main():
    """Run this test and print test output as JSON to stdout."""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument("input", help="workload result JSON file from run_workload_test.sh")
    args = aparser.parse_args()
    output = refimpl(args.input)
    if not print_loj(output):
        sys.exit(1)


if __name__ == "__main__":
    main()
