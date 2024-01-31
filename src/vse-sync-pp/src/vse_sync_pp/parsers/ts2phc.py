### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse ts2phc log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_decimal)


class TimeErrorParser(Parser):
    """Parse time error from a ts2phc log message"""
    id_ = 'ts2phc/time-error'
    elems = ('timestamp', 'interface', 'terror', 'state')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    @staticmethod
    def build_regexp(interface=None):
        """Return a regular expression string for parsing log file lines.

        If `interface` then only parse lines for the specified interface.
        """
        return r''.join((
            r'^ts2phc'
            + r'\[([1-9][0-9]*\.[0-9]{3})\]:', # timestamp
            r'(?:\s\[ts2phc\.\d\..*\])?',  # configuration file name
            fr'\s({interface})' if interface else r'\s(\S+)', # interface
            r'\smaster offset\s*',
            r'\s(-?[0-9]+)', # time error
            r'\s(\S+)', # state
            r'.*$',
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
        return self.parsed(timestamp, interface, terror, state)

    def parse_line(self, line):
        matched = self._regexp.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(2),
                matched.group(3),
                matched.group(4),
            ))
        return None
