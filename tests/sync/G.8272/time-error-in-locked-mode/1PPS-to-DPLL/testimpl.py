#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""A reference implementation for tests under:

sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL
"""

from argparse import ArgumentParser
import json

from vse_sync_pp.common import JsonEncoder
from vse_sync_pp.parsers.dpll import TimeErrorParser
from vse_sync_pp.analyzers.ppsdpll import TimeErrorAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

def refimpl(spec, filename, encoding='utf-8'):
    """A reference implementation of test:

    sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL

    Return a dict with test result, reason, analysis of logs in `filename`
    with requirements specified in `spec`.
    """
    parser = TimeErrorParser()
    analyzer = TimeErrorAnalyzer(Config.from_yaml(spec))
    with open(filename, encoding=encoding) as fid:
        analyzer.collect(*parser.parse(fid))
    return {
        'result': analyzer.result,
        'reason': analyzer.reason,
        'analysis': analyzer.analysis,
    }

def main():
    """Run this test and print test output as JSON to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('spec',help="test specification file")
    aparser.add_argument('input', help="log file to analyze")
    args = aparser.parse_args()
    output = refimpl(args.spec, args.input)
    print(json.dumps(output, cls=JsonEncoder))

if __name__ == '__main__':
    main()
