### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.analyzers"""

from unittest import TestCase
from os.path import join as joinpath
from os.path import dirname

from nose2.tools import params

from vse_sync_pp.analyzers.analyzer import (
    Config,
    CollectionIsClosed,
)

from .. import make_fqname


class TestConfig(TestCase):
    """Tests for vse_sync_pp.analyzers.analyzer.Config"""
    def test_requirement_errors(self):
        """Test vse_sync_pp.analyzers.analyzer.Config.requirement errors"""
        # no filename, no requirements
        config = Config()
        with self.assertRaises(KeyError) as ctx:
            config.requirement('foo')
        self.assertEqual(
            str(ctx.exception),
            "'no requirements specified'",
        )
        # filename, no requirements
        config = Config('bar')
        with self.assertRaises(KeyError) as ctx:
            config.requirement('baz')
        self.assertEqual(
            str(ctx.exception),
            "'no requirements specified in config file bar'",
        )
        # no filename, unknown requirements
        config = Config(requirements='quux')
        with self.assertRaises(KeyError) as ctx:
            config.requirement('corge')
        self.assertEqual(
            str(ctx.exception),
            "'unknown requirements quux'",
        )
        # filename, unknown requirements
        config = Config('quuz', 'thud')
        with self.assertRaises(KeyError) as ctx:
            config.requirement('wibble')
        self.assertEqual(
            str(ctx.exception),
            "'unknown requirements thud in config file quuz'",
        )
        # no filename, unknown requirement
        config = Config(requirements='G.8272/PRTC-A')
        with self.assertRaises(KeyError) as ctx:
            config.requirement('xxyyz')
        self.assertEqual(
            str(ctx.exception),
            "'unknown requirement xxyyz in G.8272/PRTC-A'",
        )
        # filename, unknown requirement
        config = Config(filename='foobarbaz', requirements='G.8272/PRTC-A')
        with self.assertRaises(KeyError) as ctx:
            config.requirement('quod')
        self.assertEqual(
            str(ctx.exception),
            "'unknown requirement quod in G.8272/PRTC-A"
            " in config file foobarbaz'",
        )

    def test_requirement_success(self):
        """Test vse_sync_pp.analyzers.analyzer.Config.requirement success"""
        config = Config(requirements='G.8272/PRTC-A')
        key = 'time-error-in-locked-mode/ns'
        self.assertEqual(config.requirement(key), 100)

    def test_parameter_errors(self):
        """Test vse_sync_pp.analyzers.analyzer.Config.parameter errors"""
        # no filename, no parameters
        config = Config()
        with self.assertRaises(KeyError) as ctx:
            config.parameter('foo')
        self.assertEqual(
            str(ctx.exception),
            "'no parameters specified'",
        )
        # filename, no parameters
        config = Config('bar')
        with self.assertRaises(KeyError) as ctx:
            config.parameter('baz')
        self.assertEqual(
            str(ctx.exception),
            "'no parameters specified in config file bar'",
        )
        # no filename, unknown parameters
        config = Config(parameters={'quux': 3})
        with self.assertRaises(KeyError) as ctx:
            config.parameter('corge')
        self.assertEqual(
            str(ctx.exception),
            "'unknown parameter corge'",
        )
        # filename, unknown parameters
        config = Config('quuz', parameters={'thud': 7})
        with self.assertRaises(KeyError) as ctx:
            config.parameter('wibble')
        self.assertEqual(
            str(ctx.exception),
            "'unknown parameter wibble in config file quuz'",
        )

    def test_parameter_success(self):
        """Test vse_sync_pp.analyzers.analyzer.Config.parameter success"""
        config = Config(parameters={'xxyyz': 'success'})
        self.assertEqual(config.parameter('xxyyz'), 'success')

    def test_yaml(self):
        """Test vse_sync_pp.analyzers.analyzer.Config.from_yaml"""
        filename = joinpath(dirname(__file__), 'config.yaml')
        config = Config.from_yaml(filename)
        self.assertEqual(
            config.requirement('time-error-in-locked-mode/ns'),
            100,
        )
        self.assertEqual(config.parameter('foo'), 'bar')
        self.assertEqual(config.parameter('baz'), 8)


class AnalyzerTestBuilder(type):
    """Build tests for vse_sync_pp.analyzers

    Specify this class as metaclass and provide:
    `constructor` - a callable returning the analyzer to test
    `id_` - the expected value of analyzer class attribute `id_`
    `parser` - the expected value of analyzer class attribute `parser`
    `expect` - dict of requirements, parameters, rows, result, reason,
               timestamp, duration, analysis giving test config, input data,
               expected outputs
    """
    def __new__(cls, name, bases, dct):
        constructor = dct['constructor']
        fqname = make_fqname(constructor)
        dct.update({
            'test_id': cls.make_test_id(
                constructor, fqname,
                dct['id_'],
            ),
            'test_parser': cls.make_test_parser(
                constructor, fqname,
                dct['parser'],
            ),
            'test_result': cls.make_test_result(
                constructor, fqname,
                dct['expect'],
            ),
        })
        return super().__new__(cls, name, bases, dct)

    # make functions for use as TestCase methods
    @staticmethod
    def make_test_id(constructor, fqname, id_):
        """Make a function testing id_ class attribute value"""
        def method(self):
            """Test analyzer id_ class attribute value"""
            self.assertEqual(constructor.id_, id_)
        method.__doc__ = f'Test {fqname} id_ class attribute value'
        return method

    @staticmethod
    def make_test_parser(constructor, fqname, parser):
        """Make a function testing parser class attribute value"""
        def method(self):
            """Test analyzer parser class attribute value"""
            self.assertEqual(constructor.parser, parser)
        method.__doc__ = f'Test {fqname} parser class attribute value'
        return method

    @staticmethod
    def make_test_result(constructor, fqname, expect):
        """Make a function testing analyzer test result and analysis"""
        @params(*expect)
        def method(self, dct):
            """Test analyzer test result and analysis"""
            requirements = dct['requirements']
            parameters = dct['parameters']
            rows = dct['rows']
            result = dct['result']
            reason = dct['reason']
            timestamp = dct['timestamp']
            duration = dct['duration']
            analysis = dct['analysis']
            config = Config(None, requirements, parameters)
            analyzer = constructor(config)
            analyzer.collect(*rows)
            self.assertEqual(analyzer.result, result)
            self.assertEqual(analyzer.reason, reason)
            self.assertEqual(analyzer.timestamp, timestamp)
            self.assertEqual(analyzer.duration, duration)
            self.assertEqual(analyzer.analysis, analysis)
            with self.assertRaises(CollectionIsClosed):
                analyzer.collect(*rows)
            self.assertEqual(analyzer.result, result)
            self.assertEqual(analyzer.reason, reason)
            self.assertEqual(analyzer.timestamp, timestamp)
            self.assertEqual(analyzer.duration, duration)
            self.assertEqual(analyzer.analysis, analysis)
        method.__doc__ = f'Test {fqname} analyzer test result and analysis'
        return method
