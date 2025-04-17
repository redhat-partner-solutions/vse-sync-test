### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse dpll log messages"""

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

    def parse_line(self, line):
        # DPLL samples come from a fixed format CSV file
        return self.make_parsed(line.split(','))


class SMA1TimeErrorParser(TimeErrorParser):
    id_ = 'dpll-sma1/time-error'
