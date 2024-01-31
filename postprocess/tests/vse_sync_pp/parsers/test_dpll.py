### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers.dpll"""

from unittest import TestCase
from decimal import Decimal

from vse_sync_pp.parsers.dpll import (
    TimeErrorParser,
)

from .test_parser import ParserTestBuilder


class TestTimeErrorParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.dpll.TimeErrorParser"""
    constructor = TimeErrorParser
    id_ = 'dpll/time-error'
    elems = ('timestamp', 'eecstate', 'state', 'terror')
    accept = (
        (
            '1876878.28,3,3,-0.79,-3.21',
            (Decimal('1876878.28'), 3, 3, Decimal('-0.79')),
        ),
        (
            '1876878.28,3,3,-0.79',
            (Decimal('1876878.28'), 3, 3, Decimal('-0.79')),
        ),
    )
    reject = (
        'foo bar baz',
        '3,3,-0.79',
        'quux,3,3,-0.79',
        '1876878.28,quux,3,-0.79',
        '1876878.28,3,quux,-0.79',
        '1876878.28,3,3,quux',
    )
    discard = ()
    file = (
        '\n'.join((
            '1876878.28,3,3,-0.79',
            '1876879.29,3,3,-1.05',
            '1876879.29,3,3,-0.79,-3.21',
        )),
        (
            (Decimal('1876878.28'), 3, 3, Decimal('-0.79')),
            (Decimal('1876879.29'), 3, 3, Decimal('-1.05')),
            (Decimal('1876879.29'), 3, 3, Decimal('-0.79')),
        ),
    )
