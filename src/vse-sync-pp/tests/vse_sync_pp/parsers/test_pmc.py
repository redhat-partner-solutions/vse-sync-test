### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers.pmc"""

from unittest import TestCase
from decimal import Decimal

from vse_sync_pp.parsers.pmc import (
    ClockClassParser,
)

from .test_parser import ParserTestBuilder


class TestClockClassParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.pmc.TestClockClassParser"""
    constructor = ClockClassParser
    id_ = 'phc/gm-settings'
    elems = ('timestamp', 'clock_class', 'clockAccuracy', 'offsetScaledLogVariance')
    accept = (
        #FreeRun class id: 248
        ('681011.839,248,0xFE,0xFFFF',
         (Decimal('681011.839'), 248, '0xFE', '0xFFFF'),),
        #Locked class id: 6
        ('2023-06-16T17:01:11.131Z,6,0x21,0x4E5D',
         (Decimal('1686934871.131'), 6, '0x21', '0x4E5D'),),
        #Holdover class ids: 7,140,150,160
        ('2023-06-16T17:01:11.131282-00:00,7,0xFE,0xFFFF',
         (Decimal('1686934871.131282'), 7, '0xFE', '0xFFFF'),),
        ('2023-06-16T17:01:11.131282269+00:00,140,0xFE,0xFFFF',
         (Decimal('1686934871.131282269'), 140, '0xFE', '0xFFFF'),),
        ('681011.839,150,0xFE,0xFFFF',
         (Decimal('681011.839'), 150, '0xFE', '0xFFFF'),),
        ('681011.839,160,0xFE,0xFFFF',
         (Decimal('681011.839'), 160, '0xFE', '0xFFFF'),),
    )
    reject = (
        'foo bar baz quux corge',
        'quux,3,3,xy,xyz',
        '1876878.28,quux,3,2,baz',
        '2023-06-16T17:01Z,5,-3,foo,2',
        '2023-06-16T17:01:00Z,5,-3,-1,-2',
        '2023-06-16T17:01:00.123+01:00,5,-3,foo,bar',
        '2023-06-16T17:01:00,123+00:00,5,-3,foo,bar',
    )
    discard = ()
    file = (
        '\n'.join((
            '847914.839,248,0xFE,0xFFFF',
            '847915.839,6,0x21,0x4E5D',
            '847916.839,7,0xFE,0xFFFF',
        )),
        (
            (Decimal('847914.839'), 248, '0xFE', '0xFFFF'),
            (Decimal('847915.839'), 6, '0x21', '0x4E5D'),
            (Decimal('847916.839'), 7, '0xFE', '0xFFFF'),
        ),
    )
