#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0

"""A reference implementation of test:

sync/G.8272/time-error-in-locked-mode/PRTC-A/DPLL-to-PHC
"""

from argparse import ArgumentParser
import json
from os.path import join as joinpath
from os.path import dirname

from vse_sync_pp.parsers.dpll import PhaseOffsetParser
from vse_sync_pp.analyzers.ppsdpll import PhaseOffsetTimeErrorAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

CONFIG = joinpath(dirname(__file__), 'config.yaml')

def refimpl(filename, encoding='utf-8'):
    """A reference implementation of test:

    sync/G.8272/phase-offset-time-error-in-locked-mode/PRTC-A/1PPS-to-DPLL

    Return a boolean test result from the analysis of logs in `filename`.
    """
    parser = PhaseOffsetParser()
    analyzer = PhaseOffsetTimeErrorAnalyzer(Config.from_yaml(CONFIG))
    with open(filename, encoding=encoding) as fid:
        analyzer.collect(*parser.parse(fid))
    return analyzer.result

def main():
    """Run this test and print test result as JSON boolean to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('input', help="log file to analyze")
    args = aparser.parse_args()
    result = refimpl(args.input)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
