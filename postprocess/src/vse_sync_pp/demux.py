### SPDX-License-Identifier: GPL-2.0-or-later

"""Demultiplex log messages from a single multiplexed source."""

from argparse import ArgumentParser
import sys

from .common import (
    open_input,
    print_loj,
)

from .parsers import PARSERS
from .source import muxed


def main():
    """Demultiplex log messages from a single multiplexed source.

    Demultiplex log messages for the specified parser from the multiplexed
    content in input. For each demultiplexed log message print the canonical
    data produced by the parser as JSON.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        'input',
        help="input file, or '-' to read from stdin",
    )
    aparser.add_argument(
        'parser', choices=tuple(PARSERS),
        help="data to demultiplex from input",
    )
    args = aparser.parse_args()
    parser = PARSERS[args.parser]()
    with open_input(args.input) as fid:
        for (_, data) in muxed(fid, {parser.id_: parser}):
            # Python exits with error code 1 on EPIPE
            if not print_loj(data):
                sys.exit(1)


if __name__ == '__main__':
    main()
