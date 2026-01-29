### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse ts2phc log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_decimal)


class TimeErrorParser(Parser):
    """Parse time error from ts2phc or dpll log messages.

    Supports both formats:
    - Old ts2phc format: ts2phc[681011.839]: [ts2phc.0.config] ens3f0 master offset 0 s2
    - New dpll format (PTP operator 4.16+ with e810 plugin):
      dpll[1769630949]:[ts2phc.0.config] ens3f0 frequency_status 3 offset 0 phase_status 3 pps_status 1 s2
    """
    id_ = 'ts2phc/time-error'
    elems = ('timestamp', 'interface', 'terror', 'state')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    @staticmethod
    def build_regexp_ts2phc(interface=None):
        """Return a regular expression for parsing old ts2phc log format."""
        return r''.join((
            r'^ts2phc'
            + r'\[([1-9][0-9]*\.?[0-9]*)\]:', # timestamp (with or without decimal)
            r'(?:\s\[ts2phc\.\d\..*\])?',  # configuration file name
            fr'\s({interface})' if interface else r'\s(\S+)', # interface
            r'(?:\smaster)?\s+offset\s*',
            r'\s(-?[0-9]+)', # time error
            r'\s(\S+)', # state
            r'.*$',
        ))

    @staticmethod
    def build_regexp_dpll(interface=None):
        """Return a regular expression for parsing dpll log format (e810 plugin)."""
        return r''.join((
            r'^dpll'
            + r'\[([1-9][0-9]*)\]:', # timestamp (integer, unix epoch)
            r'\[.*\]',  # configuration file name like [ts2phc.0.config]
            fr'\s({interface})' if interface else r'\s(\S+)', # interface
            r'\s+frequency_status\s+\d+',  # frequency_status field
            r'\s+offset\s+(-?[0-9]+)',  # time error (offset value)
            r'\s+phase_status\s+\d+',  # phase_status field
            r'(?:\s+pps_status\s+\d+)?',  # optional pps_status field
            r'\s+(\S+)', # state
            r'.*$',
        ))

    def __init__(self, interface=None):
        super().__init__()
        self._regexp_ts2phc = re.compile(self.build_regexp_ts2phc(interface))
        self._regexp_dpll = re.compile(self.build_regexp_dpll(interface))

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_decimal(elems[0])
        interface = str(elems[1])
        terror = int(elems[2])
        state = str(elems[3])
        return self.parsed(timestamp, interface, terror, state)

    def parse_line(self, line):
        # Try old ts2phc format first
        matched = self._regexp_ts2phc.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(2),
                matched.group(3),
                matched.group(4),
            ))
        # Try new dpll format (PTP operator 4.16+ with e810 plugin)
        matched = self._regexp_dpll.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(2),
                matched.group(3),
                matched.group(4),
            ))
        return None
