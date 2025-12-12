#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""Plot data for test under:

sync/G.8272/clock-accuracy

Visualizes observed clock class events from raw ptp daemon logs.
"""

import re
import sys
from argparse import ArgumentParser
from collections import namedtuple

from vse_sync_pp.common import (
    open_input,
    print_loj,
)
from vse_sync_pp.plot import Plotter, Axis


RE_PMC_SET = re.compile(
    r'SET GRANDMASTER_SETTINGS_NP(?:\s+[^"]*?)?'
    r'clockClass\s+(?P<class>\d+)\s+'
    r'clockAccuracy\s+(?P<accuracy>0x[0-9a-fA-F]+)'
)


def main():
    """Plot test data and print files output as JSON to stdout

    To generate an image file, supply the output image prefix (path and stem)
    followed by the input log file.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('prefix', help="output image prefix")
    aparser.add_argument('input', help="ptp daemon log file to analyze")
    args = aparser.parse_args()

    # Build simple series of (sample index, clock_class)
    Parsed = namedtuple('Parsed', ('idx', 'clock_class', 'clock_accuracy'))
    plotter = Plotter(Axis("sample", "idx"), Axis("clock class", "clock_class"))

    idx = 0
    with open_input(args.input) as fid:
        for line in fid:
            if RE_PMC_SET.search(line):
                m = RE_PMC_SET.search(line)
                try:
                    cls = int(m.group('class'))
                    acc = m.group('accuracy').upper()
                except Exception:
                    continue
                plotter.append(Parsed(idx, cls, acc))
                idx += 1

    # Generate plot
    output = f'{args.prefix}.png'
    plotter.plot_scatter(output)
    item = {
        'path': output,
        'title': "Clock class (SET GRANDMASTER_SETTINGS_NP) with parsed clockAccuracy",
    }
    # Python exits with error code 1 on EPIPE
    if not print_loj([item]):
        sys.exit(1)


if __name__ == '__main__':
    main()
