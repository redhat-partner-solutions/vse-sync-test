### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers.phc2sys"""

from unittest import TestCase
from decimal import Decimal

from vse_sync_pp.parsers.phc2sys import (
    TimeErrorParser,
)

from .test_parser import ParserTestBuilder


class TestTimeErrorParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.phc2sys.TimeErrorParser"""
    constructor = TimeErrorParser
    id_ = 'phc2sys/time-error'
    elems = ('timestamp', 'terror', 'state', 'delay')
    accept = (
        ('phc2sys[681011.839]: [ptp4l.0.config] '
         'CLOCK_REALTIME phc offset         8 s2 freq   +6339 delay    502',
         (Decimal('681011.839'), 8, 's2', 502),),
        ('phc2sys[847916.839]: '
         'CLOCK_REALTIME phc offset          4 s2 freq      +639 delay    102',
         (Decimal('847916.839'), 4, 's2', 102),),
        ('phc2sys[681011.839]: [ptp4l.0.config] '
         'CLOCK_REALTIME phc offset         8 s2 freq   -6339 delay    502',
         (Decimal('681011.839'), 8, 's2', 502),),
        ('phc2sys[681012.839]: [ptp4l.1.config] '
         'CLOCK_REALTIME phc offset         8 s2 freq   -6339 delay    502',
         (Decimal('681012.839'), 8, 's2', 502),),
        ('phc2sys[847916.839]: '
         'CLOCK_REALTIME phc offset          4 s2 freq      -639 delay    102',
         (Decimal('847916.839'), 4, 's2', 102),),
    )
    reject = ()
    discard = (
        'foo bar baz',
    )
    file = (
        '\n'.join((
            'foo',
            'phc2sys[847914.839]: [ptp4l.0.config] '
            'CLOCK_REALTIME phc offset          1 s2 freq      +639 delay    102',
            'bar',
            'phc2sys[847915.839]: [ptp4l.0.config] '
            'CLOCK_REALTIME phc offset          0 s2 freq      +639 delay    102',
            'baz',
            'phc2sys[847916.839]: '
            'CLOCK_REALTIME phc offset          4 s2 freq      -639 delay    102',
        )),
        (
            (Decimal('847914.839'), 1, 's2', 102),
            (Decimal('847915.839'), 0, 's2', 102),
            (Decimal('847916.839'), 4, 's2', 102),
        ),
    )
