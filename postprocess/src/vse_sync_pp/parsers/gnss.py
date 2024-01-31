### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse GNSS log messages"""

from collections import namedtuple

from .parser import (Parser, parse_timestamp)


class TimeErrorParser(Parser):
    """Parse time error from a GNSS CSV sample"""
    id_ = 'gnss/time-error'
    # 'state' values are assumed to be u-blox gpsFix values
    # 0 = no fix
    # 1 = dead reckoning only
    # 2 = 2D-Fix
    # 3 = 3D-Fix
    # 4 = GPS + dead reckoning combined
    # 5 = time only fix
    elems = ('timestamp', 'state', 'terror')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_timestamp(elems[0])
        state = int(elems[1])
        terror = int(elems[2])
        return self.parsed(timestamp, state, terror)

    def parse_line(self, line):
        # GNSS samples come from a fixed format CSV file
        return self.make_parsed(line.split(','))
