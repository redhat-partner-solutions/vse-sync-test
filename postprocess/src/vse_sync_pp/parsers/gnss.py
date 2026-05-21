### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse GNSS log messages"""

import re
from collections import namedtuple

from .parser import (Parser, parse_timestamp)


class TimeErrorParser(Parser):
    """Parse time error from GNSS CSV samples or linuxptp gnss log lines.

    CSV format: timestamp,state,terror

    Log format (PTP operator ts2phc):
      gnss[1779342093]:[ts2phc.0.config]  gnss_status 3 offset 2 s2
      gnss[1779342093]:[ts2phc.0.config] eno8703np0 gnss_status 3 offset 2 s2
    """
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

    _LOG_RE = re.compile(
        r'^gnss'
        r'\[([1-9][0-9]*)\]:'  # timestamp (unix epoch)
        r'\[.*\]'  # configuration file name
        r'(?:\s+(?!gnss_status)(\S+))?'  # optional interface
        r'\s+gnss_status\s+(\d+)'
        r'\s+offset\s+(-?[0-9]+)'
        r'\s+\S+'  # state (e.g. s2)
        r'.*$',
    )

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_timestamp(elems[0])
        state = int(elems[1])
        terror = int(elems[2])
        return self.parsed(timestamp, state, terror)

    def parse_line(self, line):
        matched = self._LOG_RE.match(line)
        if matched:
            return self.make_parsed((
                matched.group(1),
                matched.group(3),
                matched.group(4),
            ))
        if line.startswith(('gnss', 'dpll', 'ts2phc', 'ptp4l', 'phc2sys', 'I')):
            return None
        if ',' not in line:
            return None
        return self.make_parsed(line.split(','))
