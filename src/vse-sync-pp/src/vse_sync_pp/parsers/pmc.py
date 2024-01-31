### SPDX-License-Identifier: GPL-2.0-or-later

"""Parse PMC log messages"""

from collections import namedtuple

from .parser import (Parser, parse_timestamp)


class ClockClassParser(Parser):
    """Parse clock class samples"""
    id_ = 'phc/gm-settings'
    elems = ('timestamp', 'clock_class', 'clockAccuracy', 'offsetScaledLogVariance')
    y_name = 'clock_class'
    parsed = namedtuple('Parsed', elems)

    def make_parsed(self, elems):
        if len(elems) < len(self.elems):
            raise ValueError(elems)
        timestamp = parse_timestamp(elems[0])
        clock_class = int(elems[1])
        clock_accuracy = str(elems[2]).rstrip()
        offset_scaled_log_variance = str(elems[3]).rstrip()
        return self.parsed(timestamp, clock_class, clock_accuracy, offset_scaled_log_variance)

    def parse_line(self, line):
        # PMC samples come from a CSV file
        return self.make_parsed(line.split(','))
