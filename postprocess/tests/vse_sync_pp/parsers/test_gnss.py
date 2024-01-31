### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers.gnss"""

from unittest import TestCase
from decimal import Decimal

from vse_sync_pp.parsers.gnss import (
    TimeErrorParser,
)

from .test_parser import ParserTestBuilder


class TestTimeErrorParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.gnss.TimeErrorParser"""
    constructor = TimeErrorParser
    id_ = 'gnss/time-error'
    elems = ('timestamp', 'state', 'terror')
    accept = (
        ('681011.839,5,-3',
         (Decimal('681011.839'), 5, -3)),
        ('2023-06-16T17:01:11.131Z,1,400',
         (Decimal('1686934871.131'), 1, 400)),
        ('2023-06-16T17:01:11.131282-00:00,2,399',
         (Decimal('1686934871.131282'), 2, 399)),
        ('2023-06-16T17:01:11.131282269+00:00,3,398',
         (Decimal('1686934871.131282269'), 3, 398)),
        ('681011.839,5,-3,-2.72',
         (Decimal('681011.839'), 5, -3)),
    )
    reject = (
        'foo bar baz',
        '1876878.28,3',
        'quux,3,3',
        '1876878.28,quux,3',
        '1876878.28,3,quux',
        '2023-06-16T17:01Z,5,-3',
        '2023-06-16T17:01:00Z,5,-3',
        '2023-06-16T17:01:00.123+01:00,5,-3',
        '2023-06-16T17:01:00,123+00:00,5,-3',
    )
    discard = ()
    file = (
        '\n'.join((
            '847914.839,3,4',
            '847915.839,5,-1',
            '847915.839,5,-1,-1',

        )),
        (
            (Decimal('847914.839'), 3, 4),
            (Decimal('847915.839'), 5, -1),
            (Decimal('847915.839'), 5, -1),
        ),
    )
