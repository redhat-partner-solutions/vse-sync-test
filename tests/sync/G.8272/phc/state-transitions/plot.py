#!/usr/bin/env python3

### SPDX-License-Identifier: GPL-2.0-only

"""Plot data for test:

sync/G.8272/phc/state-transitions
"""

import sys
from argparse import ArgumentParser
import json

from vse_sync_pp.common import (
    open_input,
    print_loj,
)

from vse_sync_pp.heatmap import Heatmap

STATE_NAMES = ["FREERUN",
               "LOCKED",
               "HOLDOVER_IN_SPEC",
               "HOLDOVER_OUT_SPEC1",
               "HOLDOVER_OUT_SPEC2",
               "HOLDOVER_OUT_SPEC3",
               ]


def main():
    """Plot test data and print files output as JSON to stdout.

    To generate an image file, supply the output image prefix (path and stem)
    followed by exactly the same command line args as supplied to the reference
    implementation.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument('prefix', help="output image prefix")
    aparser.add_argument('input', help='input data file')
    args = aparser.parse_args()

    # row/column
    unallowed_cells = [(0, 2), (0, 3), (0, 4), (0, 5),
                       (1, 0), (1, 3), (1, 4), (1, 5),
                       (2, 0),
                       (3, 0), (3, 2),
                       (4, 0), (4, 2),
                       (5, 0), (5, 2)]

    heatmap = Heatmap(STATE_NAMES, STATE_NAMES, 'PHC State Transitions',
                      unallowed_cells, 'State Transition Count',
                      'To', 'From')
    with open_input(args.input) as fid:
        data = json.load(fid)

    heatmap_data = []
    clock_class_count = data['analysis']['clock_class_count']

    for state in STATE_NAMES:
        state_transitions = [transitions for transitions in clock_class_count[state]['transitions'].values()]
        heatmap_data.append(state_transitions)

    output = f'{args.prefix}.png'
    heatmap.plot(heatmap_data, output)
    item = {
        'path': output,
        'title': "PHC State Transitions",
    }
    # Python exits with error code 1 on EPIPE
    if not print_loj([item]):
        sys.exit(1)


if __name__ == '__main__':
    main()
