### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse GNSS log messages"""

import re
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

    # linuxptp: gnss[ts]:[profile] [iface] gnss_status N offset M s2
    _LOG_LINE_RE = re.compile(
        r'^.*?gnss\[([0-9]+)\]:\[[^\]]+\]\s+'
        r'(?:\S+\s+)?gnss_status\s+(-?\d+)\s+offset\s+(-?\d+)\s+(\S+)'
    )

    def parse_line(self, line):
        matched = self._LOG_LINE_RE.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(2),
                matched.group(3),
            ))
        # GNSS samples come from a fixed format CSV file
        if ',' not in line:
            return None
        return self.make_parsed(line.split(','))
