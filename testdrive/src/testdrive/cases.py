### SPDX-License-Identifier: GPL-2.0-or-later

"""Test case analysis"""

from .run import timevalue


def timing(cases):
    """Return (timestamp, duration) for test `cases`.

    If `cases` contain no timing information return (None, None). Otherwise
    return the ISO 8601 string for the earliest timestamp in `cases` for
    `timestamp`; the total number of seconds from this timestamp to the end of
    test execution for `duration`.
    """
    # result variables
    timestamp = duration = None
    # working variables
    tv_start = tv_end = duration_last = None
    for case in cases:
        if "timestamp" in case:
            try:
                tv_case = timevalue(case["timestamp"])
            except TypeError:
                # timestamp is not an ISO format string
                # skip decimal relative timestamps
                continue
            if tv_start is None:
                timestamp = case["timestamp"]
                tv_start = tv_end = tv_case
                duration_last = case["duration"]
            elif tv_case < tv_start:
                timestamp = case["timestamp"]
                tv_start = tv_case
            elif tv_end < tv_case:
                tv_end = tv_case
                duration_last = case["duration"]
    if tv_start is not None:
        duration = (tv_end - tv_start).total_seconds() + duration_last
        duration = round(duration, 6)
    return (timestamp, duration)


def summarize(cases):
    """Return a dict of summary statistics counters for test `cases`."""
    total = len(cases)
    errors = sum(1 for case in cases if case["result"] == "error")
    failures = sum(1 for case in cases if case["result"] is False)
    (timestamp, duration) = timing(cases)
    return {
        "total": total,
        "success": total - (errors + failures),
        "failure": failures,
        "error": errors,
        "timestamp": timestamp,
        "duration": duration,
    }
