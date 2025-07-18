#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""A reference implementation for test under:

sync/G.8273.2/ptp4l/port-state-transitions

"""

from argparse import ArgumentParser
from os.path import join as joinpath
from os.path import dirname
import sys

from vse_sync_pp.common import (
    open_input,
    print_loj,
)

from vse_sync_pp.parsers.ptp4l import PortStateParser
from vse_sync_pp.analyzers.ptp4l import PortStateAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

CONFIG = joinpath(dirname(__file__), 'config.yaml')


def refimpl(filename, encoding='utf-8'):
    """A reference implementation for test under:

    sync/G.8273.2/ptp4l/port-state-transitions

    Input filename accepted MUST be in canonical format.
    Return a dict with test result, reason, analysis of logs in filename.
    """
    parser = PortStateParser()
    analyzer = PortStateAnalyzer()
    transitions = []
    with open_input(filename, encoding=encoding) as fid:
        for parsed in parser.parse(fid):
            transitions.append(parsed)
    result, reason = analyzer.test(transitions)
    return {
        'result': result,
        'reason': reason,
        'timestamp': transitions[0].timestamp if transitions else None,
        'duration': transitions[-1].timestamp - transitions[0].timestamp if len(transitions) > 1 else 0,
        'analysis': {
            'port_transitions': len(transitions),
            'transitions': [{'timestamp': t.timestamp, 'port': t.port, 'from_state': t.from_state, 'to_state': t.to_state, 'event': t.event} for t in transitions]
        },
    }


def main():
    """Run this test and print test output as JSON to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('input', help="log file to analyze")
    args = aparser.parse_args()
    output = refimpl(args.input)
    # Python exits with error code 1 on EPIPE
    if not print_loj(output):
        sys.exit(1)


if __name__ == '__main__':
    main()
