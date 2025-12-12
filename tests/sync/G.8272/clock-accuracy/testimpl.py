#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""A reference implementation for test under:

sync/G.8272/clock-accuracy

Checks clock class, clock type (T-GM), and clock accuracy from raw ptp daemon logs.
"""

import re
import sys
from argparse import ArgumentParser
from datetime import datetime

from vse_sync_pp.common import (
    open_input,
    print_loj,
)



RE_PMC_SET = re.compile(
    r'SET GRANDMASTER_SETTINGS_NP(?:\s+[^"]*?)?'
    r'clockClass\s+(?P<class>\d+)\s+'
    r'clockAccuracy\s+(?P<accuracy>0x[0-9a-fA-F]+)'
)

RE_TGM_STATUS = re.compile(r'\bT-GM-STATUS\s+s\d\b')

RE_PREFIX_TS = re.compile(
    # Matches klog-style prefix: I1203 18:06:12.001709
    r'^[IWEF](?P<md>\d{4})\s+(?P<hms>\d{2}:\d{2}:\d{2}\.\d{6})'
)


def parse_prefix_ts(line):
    """Parse timestamp like 'I1203 18:06:12.001709' into datetime (UTC naive)."""
    m = RE_PREFIX_TS.match(line)
    if not m:
        return None
    month = int(m.group('md')[:2])
    day = int(m.group('md')[2:])
    # Year is not present; use current year as a best-effort
    year = datetime.utcnow().year
    # Compose ISO string and parse
    try:
        ts = datetime.strptime(f'{year:04d}-{month:02d}-{day:02d} {m.group("hms")}', '%Y-%m-%d %H:%M:%S.%f')
    except Exception:
        return None
    return ts


def refimpl(filename, encoding='utf-8'):
    """Analyze raw ptp daemon logs to validate:
    - Clock type: must observe T-GM-STATUS entries (indicates T-GM)
    - Clock class/accuracy consistency:
      class 6  -> accuracy 0x21
      class 248 -> accuracy 0xfe
    Return a dict with test result, reason, timestamp, duration, and simple analysis.
    """
    first_ts = None
    last_ts = None

    observed_tgm = False
    # Track observed pairs and mismatches
    observed_pairs = []
    illegal_accuracy = False

    with open_input(filename, encoding=encoding) as fid:
        for line in fid:
            # timestamps
            ts = parse_prefix_ts(line)
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            # T-GM status (clock type)
            if (not observed_tgm) and RE_TGM_STATUS.search(line):
                observed_tgm = True

            # Grandmaster settings (class, accuracy)
            pmc = RE_PMC_SET.search(line)
            if pmc:
                try:
                    cls = int(pmc.group('class'))
                    acc = pmc.group('accuracy').lower()
                except Exception:
                    continue
                observed_pairs.append((cls, acc))
                if cls == 6 and acc != '0x21':
                    illegal_accuracy = True
                if cls == 248 and acc != '0xfe':
                    illegal_accuracy = True

    if not observed_pairs:
        return {
            'result': False,
            'reason': 'no GRANDMASTER_SETTINGS_NP entries found',
            'timestamp': None,
            'duration': 0,
            'analysis': {},
        }

    if not observed_tgm:
        return {
            'result': False,
            'reason': 'no T-GM-STATUS entries found (clock type missing)',
            'timestamp': None if first_ts is None else first_ts.isoformat() + 'Z',
            'duration': 0 if (first_ts is None or last_ts is None) else (last_ts - first_ts).total_seconds(),
            'analysis': {
                'observed_pairs': observed_pairs,
            },
        }

    if illegal_accuracy:
        return {
            'result': False,
            'reason': 'illegal clock accuracy for observed clock class',
            'timestamp': None if first_ts is None else first_ts.isoformat() + 'Z',
            'duration': 0 if (first_ts is None or last_ts is None) else (last_ts - first_ts).total_seconds(),
            'analysis': {
                'observed_pairs': observed_pairs,
                'clock_type': 'T-GM',
            },
        }

    return {
        'result': True,
        'reason': None,
        'timestamp': None if first_ts is None else first_ts.isoformat() + 'Z',
        'duration': 0 if (first_ts is None or last_ts is None) else (last_ts - first_ts).total_seconds(),
        'analysis': {
            'observed_pairs': observed_pairs,
            'clock_type': 'T-GM',
        },
    }


def main():
    """Run this test and print test output as JSON to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('input', help="ptp daemon log file to analyze")
    args = aparser.parse_args()
    output = refimpl(args.input)
    # Python exits with error code 1 on EPIPE
    if not print_loj(output):
        sys.exit(1)


if __name__ == '__main__':
    main()
