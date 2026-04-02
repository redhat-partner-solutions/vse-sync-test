### SPDX-License-Identifier: GPL-2.0-only

"""A reference implementation for test under:

sync/G.8272/phc/state-transitions

"""

from argparse import ArgumentParser
from os.path import join as joinpath
from os.path import dirname
import sys

from vse_sync_pp.common import (
    open_input,
    print_loj,
)

from vse_sync_pp.parsers.pmc import ClockClassParser
from vse_sync_pp.analyzers.pmc import ClockStateAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

CONFIG = joinpath(dirname(__file__), 'config.yaml')


def _get_display_name(config_path):
    """Read display_name value from a YAML config file."""
    try:
        with open(config_path, encoding='utf-8') as fid:
            for line in fid:
                if line.strip().startswith('display_name:'):
                    val = line.split(':', 1)[1].strip().strip('"').strip("'")
                    return val
    except OSError:
        pass
    return ''


def refimpl(filename, encoding='utf-8'):
    """A reference implementation for test under:

    sync/G.8272/phc/state-transitions

    Input `filename` accepted MUST be in canonical format.
    Return a dict with test result, reason, analysis of logs in `filename`.
    """
    parser = ClockClassParser()
    analyzer = ClockStateAnalyzer(Config.from_yaml(CONFIG))
    with open_input(filename, encoding=encoding) as fid:
        for parsed in parser.canonical(fid):
            analyzer.collect(parsed)
    return {
        'result': analyzer.result,
        'reason': analyzer.reason,
        'timestamp': analyzer.timestamp,
        'duration': analyzer.duration,
        'analysis': analyzer.analysis,
        'pdf_display_name': _get_display_name(CONFIG),
    }


def main():
    """Run this test and print test output as JSON to stdout"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('input', help="log file to analyze in canonical format")
    args = aparser.parse_args()
    output = refimpl(args.input)
    # Python exits with error code 1 on EPIPE
    if not print_loj(output):
        sys.exit(1)


if __name__ == '__main__':
    main()
