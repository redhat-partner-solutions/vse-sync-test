### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse dpll log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_timestamp, parse_decimal)


class TimeErrorParser(Parser):
    """Parse Time Error from a dpll CSV sample"""
    id_ = 'dpll/time-error'
    elems = ('timestamp', 'eecstate', 'state', 'terror')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_timestamp(elems[0])
        eecstate = int(elems[1])
        state = int(elems[2])
        terror = parse_decimal(elems[3])
        return self.parsed(timestamp, eecstate, state, terror)

    # linuxptp: dpll[ts]:[profile] [iface] frequency_status N offset M phase_status P [pps_status Q] s2
    _LOG_LINE_RE = re.compile(
        r'^.*?dpll\[([0-9]+)\]:\[[^\]]+\]\s+'
        r'(?:\S+\s+)?frequency_status\s+(-?\d+)\s+offset\s+(-?\d+)\s+'
        r'phase_status\s+(-?\d+)(?:\s+pps_status\s+\d+)?\s+\S+'
    )

    def parse_line(self, line):
        matched = self._LOG_LINE_RE.match(line)
        if matched:
            # frequency_status -> eecstate; phase_status -> state; offset -> terror
            return self.make_parsed((
                matched.group(1),
                matched.group(2),
                matched.group(4),
                matched.group(3),
            ))
        # DPLL samples come from a fixed format CSV file
        if ',' not in line:
            return None
        return self.make_parsed(line.split(','))


class SMA1TimeErrorParser(TimeErrorParser):
    id_ = 'dpll-sma1/time-error'
