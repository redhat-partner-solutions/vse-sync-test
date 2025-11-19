### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse ptp4l log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_decimal)


class TimeErrorParser(Parser):
    """Parse time error from a ptp4l log message for boundary clock"""
    id_ = 'ptp4l/time-error'
    elems = ('timestamp', 'interface', 'terror', 'state', 'freq', 'path_delay')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    @staticmethod
    def build_regexp(interface=None):
        """Return a regular expression string for parsing ptp4l log file lines.

        If `interface` then only parse lines for the specified interface.
        """
        return r''.join((
            r'^ptp4l\[(?P<timestamp>\d+\.?\d*)\]:\s+',
            r'\[.*\.\d+\.config:?\d*\]\s*',
            r'(?P<interface>\w+)?\s+',
            r'offset\s+(?P<offset>-?\d+)\s+',
            r'(?P<servo_state>s\d)\s+',
            r'freq\s+(?P<freq_adj>[-+]?\d+)\s*',
            r'(?:path\s+delay\s+(?P<delay>\d+))?$'
        ))

    def __init__(self, interface=None):
        super().__init__()
        self._regexp = re.compile(self.build_regexp(interface))

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_decimal(elems[0])
        interface = str(elems[1])
        terror = int(elems[2])
        state = str(elems[3])
        freq = int(elems[4])
        path_delay = int(elems[5])
        return self.parsed(timestamp, interface, terror, state, freq, path_delay)

    def parse_line(self, line):
        matched = self._regexp.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),  # timestamp
                matched.group(2),  # interface
                matched.group(3),  # terror
                matched.group(4),  # state
                matched.group(5),  # freq
                matched.group(6),  # path_delay
            ))
        return None
