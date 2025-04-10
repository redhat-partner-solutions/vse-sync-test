#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""A reference implementation of test:

sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC

Use a symbolic link to specify this file as the reference implementation for a test.
"""

import sys
from argparse import ArgumentParser
from os.path import join as joinpath
from os.path import dirname

from vse_sync_pp.common import (
    open_input,
    print_loj,
)

from vse_sync_pp.parsers.ts2phc import TimeErrorParser
from vse_sync_pp.analyzers.ts2phc import MaxTimeIntervalErrorAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

CONFIG = joinpath(dirname(__file__), 'config.yaml')


def refimpl(filename, config, interface=None, encoding='utf-8'):
    """A reference implementation for tests under:

    sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC

    Return a dict with test result, reason, timestamp, duration, and analysis of logs in `filename`.
    """
    parser = TimeErrorParser(interface)
    analyzer = MaxTimeIntervalErrorAnalyzer(Config.from_yaml(config))
    with open_input(filename, encoding=encoding) as fid:
        analyzer.collect(*parser.parse(fid))
    return {
        'result': analyzer.result,
        'reason': analyzer.reason,
        'timestamp': analyzer.timestamp,
        'duration': analyzer.duration,
        'analysis': analyzer.analysis,
    }


def main():
    """Run this test and print test output as JSON to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('input', help="log file to analyze")
    aparser.add_argument('interface', help="interface to capture", default=None)
    args = aparser.parse_args()

    output = refimpl(args.input, config=CONFIG, interface=args.interface)
    # Python exits with error code 1 on EPIPE
    if not print_loj(output):
        sys.exit(1)


if __name__ == '__main__':
    main()
