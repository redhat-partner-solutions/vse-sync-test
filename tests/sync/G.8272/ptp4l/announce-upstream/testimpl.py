#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""A reference implementation for test under:

sync/G.8272/ptp4l/announce-upstream

Checks that upstream Announce messages are received around clock class changes.
"""

import re
import sys
from argparse import ArgumentParser
from datetime import datetime, timedelta

from vse_sync_pp.common import (
    open_input,
    print_loj,
)


RE_PREFIX_TS = re.compile(r'^[IWEF](?P<md>\d{4})\s+(?P<hms>\d{2}:\d{2}:\d{2}\.\d{6})')

RE_PMC_SET = re.compile(
    r'SET GRANDMASTER_SETTINGS_NP(?:\s+[^"]*?)?'
    r'clockClass\s+(?P<class>\d+)\s+'
    r'clockAccuracy\s+(?P<accuracy>0x[0-9a-fA-F]+)'
)

# Heuristics for upstream (receive) Announce messages in ptp4l logs
RE_ANNOUNCE_RX = re.compile(
    r'(?i)\b(rcvd|received).{0,32}\bannounce\b|'
    r'\bmsg(?:Type)?\s*(?:11|0x0b).{0,32}\b(rx|received)\b'
)


def parse_prefix_ts(line):
    m = RE_PREFIX_TS.match(line)
    if not m:
        return None
    month = int(m.group('md')[:2])
    day = int(m.group('md')[2:])
    year = datetime.utcnow().year
    try:
        ts = datetime.strptime(f'{year:04d}-{month:02d}-{day:02d} {m.group("hms")}', '%Y-%m-%d %H:%M:%S.%f')
    except Exception:
        return None
    return ts


def refimpl(filename, encoding='utf-8'):
    """For each clock class change event, verify at least one upstream (received) Announce nearby."""
    class_change_times = []
    last_class = None

    # First pass: detect clock class change instants
    with open_input(filename, encoding=encoding) as fid:
        for line in fid:
            ts = parse_prefix_ts(line)
            m = RE_PMC_SET.search(line)
            if m:
                try:
                    current_class = int(m.group('class'))
                except Exception:
                    continue
                if last_class is None:
                    last_class = current_class
                else:
                    if current_class != last_class:
                        if ts is not None:
                            class_change_times.append(ts)
                        last_class = current_class

    if not class_change_times:
        return {
            'result': False,
            'reason': 'no clock class change detected',
            'timestamp': None,
            'duration': 0,
            'analysis': {},
        }

    # Second pass: for each change, look for upstream Announce within window
    window_seconds = 15
    rx_hits = {t: False for t in class_change_times}
    first_ts = None
    last_ts = None
    with open_input(filename, encoding=encoding) as fid:
        for line in fid:
            ts = parse_prefix_ts(line)
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts
            if RE_ANNOUNCE_RX.search(line) and ts is not None:
                for change_ts in class_change_times:
                    if abs((ts - change_ts).total_seconds()) <= window_seconds:
                        rx_hits[change_ts] = True

    missing = [t.isoformat() + 'Z' for (t, hit) in rx_hits.items() if not hit]
    if missing:
        return {
            'result': False,
            'reason': 'missing upstream Announce near some clock changes',
            'timestamp': None if first_ts is None else first_ts.isoformat() + 'Z',
            'duration': 0 if (first_ts is None or last_ts is None) else (last_ts - first_ts).total_seconds(),
            'analysis': {
                'changes': [t.isoformat() + 'Z' for t in class_change_times],
                'missing_for_changes': missing,
                'window/s': window_seconds,
            },
        }

    return {
        'result': True,
        'reason': None,
        'timestamp': None if first_ts is None else first_ts.isoformat() + 'Z',
        'duration': 0 if (first_ts is None or last_ts is None) else (last_ts - first_ts).total_seconds(),
        'analysis': {
            'changes': [t.isoformat() + 'Z' for t in class_change_times],
            'window/s': window_seconds,
        },
    }


def main():
    """Run this test and print test output as JSON to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('input', help="linuxptp-daemon-container log file")
    args = aparser.parse_args()
    output = refimpl(args.input)
    if not print_loj(output):
        sys.exit(1)


if __name__ == '__main__':
    main()
