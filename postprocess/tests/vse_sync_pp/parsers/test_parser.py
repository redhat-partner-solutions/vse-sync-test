### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers"""

import json
from io import StringIO

from unittest import TestCase
from nose2.tools import params

from vse_sync_pp.common import JsonEncoder
from vse_sync_pp.parsers.parser import Parser

from .. import make_fqname


class TestParser(TestCase):
    """Test cases for vse_sync_pp.parsers.parser.Parser"""
    def test_make_parsed(self):
        """Test vse_sync_pp.parsers.parser.Parser.make_parsed"""
        with self.assertRaises(ValueError):
            Parser().make_parsed(())

    def test_parse_line(self):
        """Test vse_sync_pp.parsers.parser.Parser.parse_line"""
        self.assertIsNone(Parser().parse_line('foo bar baz'))


class ParserTestBuilder(type):
    """Build tests for vse_sync_pp.parsers

    Specify this class as metaclass and provide:
    `constructor` - a callable returning the parser to test
    `id_` - the expected value of parser class attribute `id_`
    `elems` - the expected value of parser class attribute `elems`
    `accept` - a sequence of 2-tuples (line, expect) the parser must accept
    `reject` - a sequence of lines the parser must reject with ValueError
    `discard` - a sequence of lines the parser must discard
    `file` - a 2-tuple (lines, expect) the parser must parse `expect` from
             `lines` presented as a file object
    """
    def __new__(cls, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        dct.update({
            'test_id': cls.make_test_id(
                constructor, fqname,
                dct['id_'],
            ),
            'test_elems': cls.make_test_elems(
                constructor, fqname,
                dct['elems'],
            ),
            'test_make_parsed': cls.make_test_make_parsed(
                constructor, fqname,
                dct['accept'][0][1],
                dct.get("constructor_kwargs", {}),
            ),
            'test_accept': cls.make_test_accept(
                constructor, fqname,
                dct['elems'], dct['accept'],
                dct.get("constructor_kwargs", {}),
            ),
            'test_reject': cls.make_test_reject(
                constructor, fqname,
                dct['reject'],
                dct.get("constructor_kwargs", {}),
            ),
            'test_discard': cls.make_test_discard(
                constructor, fqname,
                dct['discard'],
                dct.get("constructor_kwargs", {}),
            ),
            'test_file': cls.make_test_file(
                constructor, fqname,
                dct['file'][0], dct['file'][1],
                dct.get("constructor_kwargs", {}),
            ),
            'test_canonical': cls.make_test_canonical(
                constructor, fqname,
                dct['file'][1],
                dct.get("constructor_kwargs", {}),
            ),
        })
        return super().__new__(cls, name, bases, dct)

    # make functions for use as TestCase methods
    @staticmethod
    def make_test_id(constructor, fqname, id_):
        """Make a function testing id_ class attribute value"""
        def method(self):
            """Test parser id_ class attribute value"""
            self.assertEqual(constructor.id_, id_)
        method.__doc__ = f'Test {fqname} id_ class attribute value'
        return method

    @staticmethod
    def make_test_elems(constructor, fqname, elems):
        """Make a function testing elems class attribute value"""
        def method(self):
            """Test parser elems class attribute value"""
            self.assertEqual(constructor.elems, elems)
            self.assertIn('timestamp', elems)
            self.assertIn(constructor.y_name, elems)
        method.__doc__ = f'Test {fqname} elems class attribute value'
        return method

    @staticmethod
    def make_test_make_parsed(constructor, fqname, expect, constructor_kwargs):
        """Make a function testing parser makes parsed"""
        def method(self):
            """Test parser makes parsed"""
            parser = constructor(**constructor_kwargs)
            self.assertEqual(parser.make_parsed(expect), expect)
            with self.assertRaises(ValueError):
                parser.make_parsed(expect[:-1])
        method.__doc__ = f'Test {fqname} make parsed'
        return method

    @staticmethod
    def make_test_accept(constructor, fqname, elems, accept, constructor_kwargs):
        """Make a function testing parser accepts line"""
        @params(*accept)
        def method(self, line, expect):
            """Test parser accepts line"""
            parser = constructor(**constructor_kwargs)
            parsed = parser.parse_line(line)
            # test parsed value as a tuple
            self.assertEqual(expect, parsed)
            # test parsed value as a namedtuple
            for (idx, name) in enumerate(elems):
                self.assertEqual(expect[idx], getattr(parsed, name))
        method.__doc__ = f'Test {fqname} accepts line'
        return method

    @staticmethod
    def make_test_reject(constructor, fqname, reject, constructor_kwargs):
        """Make a function testing parser rejects line"""
        @params(*reject)
        def method(self, line):
            """Test parser rejects line"""
            parser = constructor(**constructor_kwargs)
            with self.assertRaises(ValueError):
                parser.parse_line(line)
        method.__doc__ = f'Test {fqname} rejects line'
        return method

    @staticmethod
    def make_test_discard(constructor, fqname, discard, constructor_kwargs):
        """Make a function testing parser discards line"""
        @params(*discard)
        def method(self, line):
            """Test parser discards line"""
            parser = constructor(**constructor_kwargs)
            parsed = parser.parse_line(line)
            self.assertIsNone(parsed)
        method.__doc__ = f'Test {fqname} discards line'
        return method

    @staticmethod
    def make_test_file(constructor, fqname, lines, expect, constructor_kwargs):
        """Make a function testing parser parses `expect` from `lines`"""
        def method(self):
            """Test parser parses file"""
            ### parse presented timestamps
            parser = constructor(**constructor_kwargs)
            parsed = parser.parse(StringIO(lines))
            for pair in zip(parsed, expect, strict=True):
                self.assertEqual(pair[0], pair[1])
            ### parse relative timestamps
            tidx = parser.elems.index('timestamp')

            def relative(expect):
                """Generator yielding items with relative timestamps"""
                tzero = None
                for item in expect:
                    ritem = list(item)
                    if tzero is None:
                        tzero = item[tidx]
                    ritem[tidx] = item[tidx] - tzero
                    yield tuple(ritem)
            parser = constructor(**constructor_kwargs)
            parsed = parser.parse(StringIO(lines), relative=True)
            for pair in zip(parsed, relative(expect), strict=True):
                self.assertEqual(pair[0], pair[1])
        method.__doc__ = f'Test {fqname} parses file'
        return method

    @staticmethod
    def make_test_canonical(constructor, fqname, expect, constructor_kwargs):
        """Make a function testing parser parses `expect` from `expect`"""
        def method(self):
            """Test parser parses canonical"""
            lines = '\n'.join((
                json.dumps(e, cls=JsonEncoder) for e in expect
            )) + '\n'
            parser = constructor(**constructor_kwargs)
            parsed = parser.canonical(StringIO(lines))
            for pair in zip(parsed, expect, strict=True):
                self.assertEqual(pair[0], pair[1])
        method.__doc__ = f'Test {fqname} parses canonical'
        return method
