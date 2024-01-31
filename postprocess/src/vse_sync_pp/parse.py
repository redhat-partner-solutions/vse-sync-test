### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse log messages from a single source."""

from argparse import ArgumentParser
import sys

from .common import (
    open_input,
    print_loj,
)

from .parsers import PARSERS


def main():
    """Parse log messages from a single source.

    Parse log messages using the specified parser. For each parsed log message
    print the canonical data produced by the parser as JSON.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        '-r', '--relative', action='store_true',
        help="print timestamps relative to the first line's timestamp",
    )
    aparser.add_argument(
        'input',
        help="input file, or '-' to read from stdin",
    )
    aparser.add_argument(
        'parser', choices=tuple(PARSERS),
        help="data to parse from input",
    )
    args = aparser.parse_args()
    parser = PARSERS[args.parser]()
    with open_input(args.input) as fid:
        for data in parser.parse(fid, relative=args.relative):
            # Python exits with error code 1 on EPIPE
            if not print_loj(data):
                sys.exit(1)


if __name__ == '__main__':
    main()
