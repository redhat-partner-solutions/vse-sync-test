#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""Plot data for tests under:

sync/G.8272/wander-MTIE-in-locked-mode/DPLL-to-PHC

Use a symbolic link to specify this file as the plotter for a test.
"""

import sys
from argparse import ArgumentParser
from os.path import join as joinpath
from os.path import dirname

from vse_sync_pp.common import (
    open_input,
    print_loj,
)
from collections import namedtuple

from vse_sync_pp.plot import Plotter, Axis

from vse_sync_pp.parsers.ts2phc import TimeErrorParser
from vse_sync_pp.analyzers.ts2phc import MaxTimeIntervalErrorAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

CONFIG = joinpath(dirname(__file__), 'config.yaml')


def plot_data(analyzer, output):
    """Plot data"""
    plotter = Plotter(Axis("tau observation window (s)", "tau", "log"), Axis("filtered MTIE (ns)", "tdev"))
    Parsed = namedtuple('Parsed', ('tau', 'tdev'))
    for tau, sample in analyzer.toplot():
        plotter.append(Parsed(tau, sample))
    plotter.plot_scatter(output)


def main():
    """Plot test data and print files output as JSON to stdout

    To generate an image file, supply the output image prefix (path and stem)
    followed by exactly the same command line args as supplied to the reference
    implementation.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('prefix', help="output image prefix")
    aparser.add_argument('input')
    args = aparser.parse_args()

    # get data for plot from analyzer
    parser = TimeErrorParser()
    analyzer = MaxTimeIntervalErrorAnalyzer(Config.from_yaml(CONFIG))
    with open_input(args.input) as fid:
        analyzer.collect(*parser.parse(fid))

    # plot data
    output = f'{args.prefix}.png'
    plot_data(analyzer, output)
    item = {
        'path': output,
        'title': "DPLL-to-PHC MTIE (filtered)",
    }
    # Python exits with error code 1 on EPIPE
    if not print_loj([item]):
        sys.exit(1)


if __name__ == '__main__':
    main()
