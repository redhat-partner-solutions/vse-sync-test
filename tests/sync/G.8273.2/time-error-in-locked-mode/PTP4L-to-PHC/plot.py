#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""Plot data for tests under:

sync/G.8273.2/time-error-in-locked-mode/PTP4L-to-PHC

Use a symbolic link to specify this file as the plotter for a test.
"""

import sys
from argparse import ArgumentParser

from vse_sync_pp.common import (
    open_input,
    print_loj,
)

from vse_sync_pp.parsers.ptp4l import TimeErrorParser
from vse_sync_pp.plot import Plotter, Axis, TIMESERIES


def main():
    """Plot test data and print files output as JSON to stdout

    To generate an image file, supply the output image prefix (path and stem)
    followed by exactly the same command line args as supplied to the reference
    implementation.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('prefix', help="output image prefix")
    aparser.add_argument('input')
    #aparser.add_argument('interface', help="interface to capture", default=None)
    args = aparser.parse_args()
    parser = TimeErrorParser("")
    plotter = Plotter(TIMESERIES, Axis("Unfiltered Time Error (ns)", parser.y_name))
    with open_input(args.input) as fid:
        for parsed in parser.parse(fid, relative=True):
            plotter.append(parsed)
    output = f'{args.prefix}.png'
    plotter.plot(output)
    item = {
        'path': output,
        'title': "PTP4L-to-PHC Time Error (unfiltered)",
    }
    # Python exits with error code 1 on EPIPE
    if not print_loj([item]):
        sys.exit(1)


if __name__ == '__main__':
    main()
