#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""Plot data for tests under:

sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL

Use a symbolic link to specify this file as the plotter for a test.
"""

import sys
from argparse import ArgumentParser
from os.path import join as joinpath
from os.path import dirname

import numpy as np
import matplotlib.pyplot as plt

from vse_sync_pp.common import (
    open_input,
    print_loj,
)

from vse_sync_pp.parsers.dpll import TimeErrorParser
from vse_sync_pp.analyzers.ppsdpll import TimeErrorAnalyzer
from vse_sync_pp.analyzers.analyzer import Config

CONFIG = joinpath(dirname(__file__), 'config.yaml')

def plot(filename, x_name, x_data, y_name, y_data, y_desc, analyzer):
    """Plot data to `filename`"""
    fig, (ax1, ax2) = plt.subplots(2, constrained_layout=True)
    fig.set_size_inches(10, 8)
    ax1.axhline(0, color='black')
    ax1.axhline(analyzer._unacceptable, color='red')
    ax1.axhline(-analyzer._unacceptable, color='red')
    if any((abs(v) > 10 for v in y_data)):
        ax1.set_yscale('symlog', linthresh=10)
    y_good = [
        v if abs(v) <= analyzer._unacceptable else None
        for v in y_data
    ]
    ax1.plot(x_data, y_good, '.')
    y_fail = [
        v if abs(v) > analyzer._unacceptable else None
        for v in y_data
    ]
    ax1.plot(x_data, y_fail, 'rx')
    ax1.grid()
    ax1.set_title(f'{x_name} vs {y_desc}')
    counts, bins = np.histogram(
        np.array(y_data, dtype=float),
        bins='scott',
    )
    ax2.hist(bins[:-1], bins, weights=counts)
    ax2.axvline(analyzer._unacceptable, color='red')
    ax2.axvline(-analyzer._unacceptable, color='red')
    ax2.set_yscale('symlog', linthresh=10)
    ax2.set_title(f'Histogram of {y_desc}')
    plt.savefig(filename)

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
    parser = TimeErrorParser()
    analyzer = TimeErrorAnalyzer(Config.from_yaml(CONFIG))
    x_name = 'timestamp'
    y_name = parser.y_name
    y_desc = "Time Error (unfiltered)"
    x_data = []
    y_data = []
    with open_input(args.input) as fid:
        for parsed in parser.canonical(fid, relative=True):
            x_data.append(getattr(parsed, x_name))
            y_data.append(getattr(parsed, y_name))
    output = f'{args.prefix}.png'
    plot(output, x_name, x_data, y_name, y_data, y_desc, analyzer)
    item = {
        'path': output,
        'title': "1PPS-to-DPLL Time Error (unfiltered)",
    }
    # Python exits with error code 1 on EPIPE
    if not print_loj([item]):
        sys.exit(1)

if __name__ == '__main__':
    main()
