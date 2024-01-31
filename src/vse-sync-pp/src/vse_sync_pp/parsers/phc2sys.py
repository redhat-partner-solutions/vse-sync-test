### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse phc2sys log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_decimal)


class TimeErrorParser(Parser):
    """Parse time error from a phc2sys log message"""
    id_ = 'phc2sys/time-error'
    elems = ('timestamp', 'terror', 'state', 'delay')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    @staticmethod
    def build_regexp():
        """Return a regular expression string for parsing phc2sys log file lines"""
        return r'\s'.join((r'^phc2sys'
                          + r'\[([1-9][0-9]*\.[0-9]{3})\]:'  # timestamp
                          + r'(?:\s\[ptp4l\.\d\..*\])?',  # configuration file name
                            r'CLOCK_REALTIME phc offset\s*',
                            r'(-?[0-9]+)', # time error
                            r'(\S+)', # state
                            r'freq\s*',
                            r'([-+]?[0-9]+)', # frequency error
                            r'delay\s*',
                            r'(-?[0-9]+)' # delay
                          + r'\s*.*$'))

    def __init__(self):
        super().__init__()
        self._regexp = re.compile(self.build_regexp())

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_decimal(elems[0])
        terror = int(elems[1])
        state = str(elems[2])
        delay = int(elems[3])
        return self.parsed(timestamp, terror, state, delay)

    def parse_line(self, line):
        matched = self._regexp.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(2),
                matched.group(3),
                matched.group(5),
            ))
        return None
