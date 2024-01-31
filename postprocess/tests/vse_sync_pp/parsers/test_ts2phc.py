### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers.ts2phc"""

from unittest import TestCase
from decimal import Decimal

from vse_sync_pp.parsers.ts2phc import (
    TimeErrorParser,
)

from .test_parser import ParserTestBuilder


class TestTimeErrorParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.ts2phc.TimeErrorParser"""
    constructor = TimeErrorParser
    id_ = 'ts2phc/time-error'
    elems = ('timestamp', 'interface', 'terror', 'state')
    accept = (
        ('ts2phc[681011.839]: [ts2phc.0.config] '
         'ens7f1 master offset          0 s2 freq      -0',
         (Decimal('681011.839'), 'ens7f1', 0, 's2'),),
        ('ts2phc[681011.839]: [ts2phc.2.config] '
         'ens7f1 master offset          0 s2 freq      -0',
         (Decimal('681011.839'), 'ens7f1', 0, 's2'),),
        ('ts2phc[681011.839]: '
         'ens7f1 master offset          0 s2 freq      -0',
         (Decimal('681011.839'), 'ens7f1', 0, 's2'),),
    )
    reject = ()
    discard = (
        'foo bar baz',
    )
    file = (
        '\n'.join((
            'foo',
            'ts2phc[847914.839]: [ts2phc.0.config] '
            'ens7f1 master offset          1 s2 freq      +1',
            'bar',
            'ts2phc[847915.839]: [ts2phc.0.config] '
            'ens7f1 master offset          0 s2 freq      -0',
            'baz',
        )),
        (
            (Decimal('847914.839'), 'ens7f1', 1, 's2'),
            (Decimal('847915.839'), 'ens7f1', 0, 's2'),
        ),
    )
