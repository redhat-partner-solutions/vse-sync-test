### SPDX-License-Identifier: GPL-2.0-or-later

"""Common parser functionality"""

import json
import re
from datetime import (datetime, timezone)
from decimal import (Decimal, InvalidOperation)

# sufficient regex to extract the whole decimal fraction part
RE_ISO8601_DECFRAC = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.(\d+)(.*)$'
)


def parse_timestamp_abs(val):
    """Return a :class:`Decimal` from `val`, an absolute timestamp string.

    Accepted absolute timestamp strings are ISO 8601 format with restrictions.
    The string must: explicitly specify UTC timezone, supply time in seconds,
    specify a decimal fractional part with a decimal mark of '.'.

    Return None if `val` is not a string or is not an ISO 8601 format string.
    Raise :class:`ValueError` otherwise.
    """
    try:
        dtv = datetime.fromisoformat(val)
    except TypeError:
        return None
    except ValueError:
        # before Python 3.11 `fromisoformat` fails if UTC denoted by 'Z' and/or
        # the decimal fraction has more than 6 digits
        match = RE_ISO8601_DECFRAC.match(val)
        if match is None:
            return None
        # parse without decimal fraction, with 'Z' substituted
        tzv = '+00:00' if match.group(3) == 'Z' else match.group(3)
        dtv = datetime.fromisoformat(match.group(1) + tzv)
    else:
        match = RE_ISO8601_DECFRAC.match(val)
        if match is None:
            raise ValueError(val)
    if dtv.tzinfo != timezone.utc:
        raise ValueError(val)
    # `dtv` may truncate decimal fraction: use decimal fraction from `val`
    return Decimal(f'{int(dtv.timestamp())}.{match.group(2)}')


def parse_decimal(val):
    """Return a :class:`Decimal` from `val` or raise :class:`ValueError`"""
    try:
        return Decimal(val)
    except InvalidOperation as exc:
        raise ValueError(val) from exc


def parse_timestamp(val):
    """Return a :class:`Decimal` from absolute or relative timestamp `val`"""
    return parse_timestamp_abs(val) or parse_decimal(val)


def relative_timestamp(parsed, tzero):
    """Return relative timestamp with respect to `tzero` coming from `parsed`"""
    timestamp = getattr(parsed, 'timestamp', None)
    if timestamp is not None:
        if tzero is None:
            tzero = timestamp
        parsed = parsed._replace(timestamp=timestamp - tzero)
    return tzero, parsed


class Parser():
    """A base class providing common parser functionality"""
    def make_parsed(self, elems):
        """Return a namedtuple value from parsed iterable `elems`.

        Raise :class:`ValueError` if a value cannot be formed from `elems`.
        """
        raise ValueError(elems)

    def parse_line(self, line):
        """Parse `line`.

        If `line` is accepted, return a namedtuple value.
        If `line` is rejected, raise :class:`ValueError`.
        Otherwise the `line` is discarded, return None.
        """
        return None

    def parse(self, file, relative=False):
        """Parse lines from `file` object.

        This method is a generator yielding a namedtuple value for each
        accepted line in `file`. If `relative` is truthy, then present all
        timestamps relative to the first accepted line's timestamp.
        """
        tzero = None
        for line in file:
            parsed = self.parse_line(line)
            if parsed is not None:
                if relative:
                    tzero, parsed = relative_timestamp(parsed, tzero)
                yield parsed

    def canonical(self, file, relative=False):
        """Parse canonical data from `file` object.

        The canonical representation is JSON-encoded parsed data, with one
        parsed item per line in `file`. If `relative` is truthy, then present
        all timestamps relative to the first accepted line's timestamp.

        This method is a generator yielding a namedtuple value for each line in
        `file`.
        """
        tzero = None
        for line in file:
            obj = json.loads(line, parse_float=Decimal)
            parsed = self.make_parsed(obj)
            if parsed is not None:
                if relative:
                    tzero, parsed = relative_timestamp(parsed, tzero)
                yield parsed
