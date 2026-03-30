### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse ts2phc log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_decimal)


class TimeErrorParser(Parser):
    """Parse time error from ts2phc log messages.

    The interface parameter can be a single string, or an iterable of strings
    to match any of several identifiers (e.g. both a PTP clock path like
    /dev/ptp4 and a network interface name like ens3f0).
    """
    id_ = 'ts2phc/time-error'
    elems = ('timestamp', 'interface', 'terror', 'state')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    @staticmethod
    def _interface_pattern(interface):
        """Return a regex fragment matching one or more interface identifiers.

        Accepts None (match any non-whitespace token), a single string,
        or an iterable of strings (match any of them).
        """
        if interface is None:
            return r'\s(\S+)'
        if isinstance(interface, str):
            return fr'\s({interface})'
        identifiers = [i for i in interface if i]
        if not identifiers:
            return r'\s(\S+)'
        if len(identifiers) == 1:
            return fr'\s({identifiers[0]})'
        return fr'\s({"|".join(identifiers)})'

    @staticmethod
    def build_regexp(interface=None):
        """Return a regular expression for parsing ts2phc log format."""
        return r''.join((
            r'^ts2phc'
            + r'\[([1-9][0-9]*\.?[0-9]*)\]:', # timestamp (with or without decimal)
            r'(?:\s\[ts2phc\.\d\..*\])?',  # configuration file name
            TimeErrorParser._interface_pattern(interface),
            r'(?:\smaster)?\s+offset\s*',
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
