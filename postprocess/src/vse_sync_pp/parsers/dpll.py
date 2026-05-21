### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse dpll log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_timestamp, parse_decimal)


class TimeErrorParser(Parser):
    """Parse time error from DPLL CSV samples or linuxptp dpll log lines.

    CSV format: timestamp,eecstate,state,terror[,eecterror]

    Log format (PTP operator 4.16+):
      dpll[1779342093]:[ts2phc.0.config] eno8703np0 frequency_status 3 offset 2 phase_status 3 pps_status 1 s2
    """
    id_ = 'dpll/time-error'
    elems = ('timestamp', 'eecstate', 'state', 'terror')
    y_name = 'terror'
    parsed = namedtuple('Parsed', elems)

    _LOG_RE = re.compile(
        r'^dpll'
        r'\[([1-9][0-9]*)\]:'  # timestamp (unix epoch)
        r'\[.*\]'  # configuration file name
        r'\s+(\S+)'  # interface
        r'\s+frequency_status\s+(\d+)'
        r'\s+offset\s+(-?[0-9]+)'
        r'\s+phase_status\s+(\d+)'
        r'(?:\s+pps_status\s+\d+)?'
        r'\s+\S+'  # state (e.g. s2)
        r'.*$',
    )

    def __init__(self, interface=None):
        super().__init__()
        if interface is None:
            self._log_re = self._LOG_RE
        else:
            self._log_re = re.compile(
                self._LOG_RE.pattern.replace(
                    r'\s+(\S+)',
                    fr'\s+({re.escape(interface)})',
                    1,
                )
            )

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_timestamp(elems[0])
        eecstate = int(elems[1])
        state = int(elems[2])
        terror = parse_decimal(elems[3])
        return self.parsed(timestamp, eecstate, state, terror)

    def parse_line(self, line):
        matched = self._log_re.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(3),
                matched.group(5),
                matched.group(4),
            ))
        if line.startswith(('gnss', 'dpll', 'ts2phc', 'ptp4l', 'phc2sys', 'I')):
            return None
        if ',' not in line:
            return None
        return self.make_parsed(line.split(','))


class SMA1TimeErrorParser(TimeErrorParser):
    id_ = 'dpll-sma1/time-error'
