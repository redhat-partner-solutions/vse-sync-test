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
        r'^ptp4l\[(?P<timestamp>\d+\.?\d*)\]:\s+\[.*\.\d+\.config:?\d*\]\s*(?P<interface>\w+)?\s+offset\s+(?P<offset>-?\d+)\s+(?P<servo_state>s\d)\s+freq\s+(?P<freq_adj>[-+]?\d+)\s*(?:path\s+delay\s+(?P<delay>\d+))?$'
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


#class PortStateParser(Parser):
#    """Parse port state transitions from ptp4l log messages"""
#    id_ = 'ptp4l/port-state'
#    elems = ('timestamp', 'port', 'from_state', 'to_state', 'event')
#    y_name = 'to_state'
    #parsed = namedtuple('Parsed', elems)

   # @staticmethod
   # def build_regexp():
   #     """Return a regular expression string for parsing ptp4l port state transitions"""
   #     return r''.join((
   #         r'^ptp4l'
   #         + r'\[([1-9][0-9]*\.[0-9]{3})\]:', # timestamp
   #         r'(?:\s\[ptp4l\.\d\..*\])?',  # configuration file name
   #         r'\s+port\s+([0-9]+):', # port number
   #         r'\s+(\w+)\s+to\s+(\w+)\s+on\s+(\w+)', # state transition
   #         r'.*$',
   #     ))

    #def __init__(self):
    #    super().__init__()
    #    self._regexp = re.compile(self.build_regexp())

    #def make_parsed(self, elems):
    #    if len(elems) < len(self.elems):
    #        raise ValueError(elems)
    #    timestamp = parse_decimal(elems[0])
    #    port = int(elems[1])
    #    from_state = str(elems[2])
    #    to_state = str(elems[3])
    #    event = str(elems[4])
    #    return self.parsed(timestamp, port, from_state, to_state, event)

    #def parse_line(self, line):
    #    matched = self._regexp.match(line)
    #    if matched:
    #        return self.make_parsed((
    #            matched.group(1),  # timestamp
    #            matched.group(2),  # port
    #            matched.group(3),  # from_state
    #            matched.group(4),  # to_state
    #            matched.group(5),  # event
     #       ))
    #    return None 