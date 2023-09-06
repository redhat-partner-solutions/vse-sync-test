#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""Plot data for test:

sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL
"""

from argparse import ArgumentParser
from os.path import join as joinpath
from os.path import dirname

from vse_sync_pp.common import open_input
from vse_sync_pp.parsers.dpll import TimeErrorParser
from vse_sync_pp.plot import Plotter

def main():
    """Plot data for this test to an image file.

    To generate an image file, supply the same input data file(s) and in the same order as they were
    presented to the reference implementation.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('output', help="output image file")
    aparser.add_argument('input', help="input data file")
    args = aparser.parse_args()
    parser = TimeErrorParser()
    plotter = Plotter(parser.y_name, "Time Error (unfiltered)")
    with open_input(args.input) as fid:
            for parsed in parser.canonical(fid):
                plotter.append(parsed)
    plotter.plot(args.output)

if __name__ == '__main__':
    main()
