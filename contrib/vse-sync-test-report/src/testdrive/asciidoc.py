### SPDX-License-Identifier: GPL-2.0-or-later

"""Generate asciidoc output from JUnit inputs"""

from argparse import ArgumentParser
from collections import OrderedDict
import os
from shutil import copyfile
import json
from uuid import uuid4
from decimal import Decimal
from xml.etree import ElementTree as ET


class Config(dict):
    """Configuration of asciidoc generation."""

    def case_path(self, case):
        """Return a path in the local filesystem to the files for `case`.

        This function only computes the path given configuration variables:
        it does not guarantee that the path exists or has required files.
        """
        try:
            suite = self['suites'][case.suite]
            baseurl = suite['baseurl']
            # Prefer canonical tree URL (JUnit property test_directory_url) when
            # test_id is human-readable only.
            candidate = case.get('test_directory_url') or case.get('test_id')
            if candidate and candidate.startswith(baseurl):
                return os.path.join(
                    self['repositories'][suite['repository']],
                    candidate.split(baseurl, maxsplit=1)[1].split("?")[0].lstrip('/'),
                )
        except KeyError:
            pass
        return None

    def case_path_testspec(self, case):
        """Return a path in the local filesystem to the test spec for `case`.

        Return None if the path could not be computed or there is not a regular
        file at that path.
        """
        try:
            path = os.path.join(self.case_path(case), 'testspec.adoc')
            if os.path.isfile(path):
                return path
        except TypeError:
            pass
        return None

    def case_title(self, case):
        """Return test case title for `case`.

        Return the text for the first title in the testspec.adoc file for this
        `case`. Otherwise return `case.name`.
        """
        path = self.case_path_testspec(case)
        if path:
            with open(path, encoding='utf-8') as fid:
                for line in fid:
                    if line.startswith('='):
                        return line.lstrip('= ').rstrip()
        return case.name

    @classmethod
    def json(cls, filename, encoding='utf-8'):
        """Return a new instance from JSON-encoded config in `filename`."""
        with open(filename, encoding=encoding) as fid:
            return cls(json.load(fid))


NOT_RECORDED = '[.deemphasize]_not recorded_'
EMPTY = '[.deemphasize]#-#'


def pdf_test_identifier_cell(case):
    """AsciiDoc for *test identifier* table cell: same visible name, clickable GitHub link."""
    display = case.get('test_id')
    url = case.get('test_directory_url')
    if url and display:
        safe = display.replace(']', '\\]')
        return f'link:{url}[{safe}]'
    return display or NOT_RECORDED


def a_test_success(val):
    """Return asciidoc marking `val` as test success."""
    return f'[.test-success]#{val}#'


def a_test_failure(val):
    """Return asciidoc marking `val` as test failure."""
    return f'[.test-failure]#{val}#'


def a_test_error(val):
    """Return asciidoc marking `val` as test error."""
    return f'[.test-error]#{val}#'


def literal_block(val):
    """Return asciidoc marking `val` as a literal block."""
    return '\n'.join(('', '....', val, '....'))


def row(*cells):
    """Return a string for an asciidoc table row with `cells`."""
    return '\n|\n' + '\n|\n'.join((str(c) for c in cells))


def indent_titles(filename, level):
    """Indent titles in `filename` such that the first title is at `level`.

    The first title is assumed to have the highest level title in `filename`.
    """
    with open(filename, encoding='utf-8') as fid:
        content = fid.readlines()
    indent = 0
    for line in content:
        first = 0
        for char in line:
            if char != '=':
                break
            first += 1
        if first:
            indent = len(level) - first
            break
    if indent <= 0:
        return
    prefix = '=' * indent
    with open(filename, encoding='utf-8', mode='w') as fod:
        for line in content:
            if line.startswith('='):
                line = prefix + line
            print(line, file=fod, end='')


class TestCase(dict):
    """A test case."""

    def __init__(self, elem):
        super().__init__()
        self._uuid = uuid4()
        self._name = elem.get('name')
        self._suite = elem.get('classname')
        self._timestamp = elem.get('timestamp')
        time = elem.get('time')
        self._duration = Decimal(time) if time is not None else time
        (self._result, self._reason) = self._result_reason_from_elem(elem)
        self._stdout = self._stdout_from_elem(elem)
        # put each property pair into this test case as a dict
        properties = elem.find('properties')
        if properties is not None:
            for child in properties.findall('property'):
                self[child.get('name')] = child.get('value')
        if not self._timestamp or self._duration is None:
            self._use_timing_from_stdout()

    @staticmethod
    def _result_reason_from_elem(elem):
        """Return test case (result, reason) from `elem`."""
        child = elem.find('failure')
        if child is not None:
            return (False, child.get('message'))
        child = elem.find('error')
        if child is not None:
            return ('error', child.get('message'))
        return (True, None)

    @staticmethod
    def _stdout_from_elem(elem):
        """Return test case output from `elem`."""
        child = elem.find('system-out')
        return child.text if child is not None else None

    def _use_timing_from_stdout(self):
        """Set timestamp and duration from JSON object in stdout."""
        try:
            dct = json.loads(self.stdout)
            timestamp = dct.get('timestamp')
        except (TypeError, json.JSONDecodeError, AttributeError):
            return
        if timestamp:
            self._timestamp = timestamp
            self._duration = dct['duration']

    @property
    def uuid(self):
        """A uuid for this test case."""
        return self._uuid

    @property
    def name(self):
        """The name of this test case."""
        return self._name

    @property
    def suite(self):
        """The test suite name of this test case."""
        return self._suite

    @property
    def timestamp(self):
        """The timestamp of this test case."""
        return self._timestamp

    @property
    def duration(self):
        """The duration of this test case."""
        return self._duration

    @property
    def result(self):
        """The result of this test case."""
        return self._result

    @property
    def a_result(self):
        """The result of this test case as asciidoc."""
        if self.result is True:
            return a_test_success('success')
        if self.result is False:
            return a_test_failure('failure')
        return a_test_error(self.result)

    @property
    def reason(self):
        """The reason of this test case."""
        return self._reason

    @property
    def stdout(self):
        """The output of this test case."""
        return self._stdout

    @property
    def anchor_result(self):
        """Return an anchor for this test case result."""
        return f'[#{self.uuid}_result]'

    @property
    def xref_result(self):
        """Return a cross-reference to this test case result."""
        return f'<<{self.uuid}_result>>'

    @property
    def anchor_spec(self):
        """Return an anchor for this test case specification."""
        return f'[#{self.uuid}_spec]'

    @property
    def xref_spec(self):
        """Return a cross-reference to this test case specification."""
        return f'<<{self.uuid}_spec>>'


class TestDetail:
    """Test detail for a test case."""

    def __init__(self, images=(), tables=()):
        self._images = images
        self._tables = tables

    def to_asciidoc(self, objdir):
        """Generate asciidoc for this test detail.

        Any image files will be copied to a unique filename in `objdir`/images.
        """
        for (title, path) in self._images:
            filename = f'{uuid4()}{os.path.splitext(path)[1]}'
            copyfile(path, os.path.join(objdir, 'pdf-assets/images', filename))
            yield ''
            yield f'.{title or os.path.basename(path)}'
            yield f'image::{filename}[]'
        for (title, dct) in self._tables:
            yield ''
            yield f'.{title}'
            yield '[cols="1,4"]'
            yield '|==='
            yield ''
            yield from (row(f'*{k}*', dct[k]) for k in sorted(dct))
            yield ''
            yield '|==='

    @staticmethod
    def _image_item(item):
        """Return (title, path) for the image specified by `item`.

        Return None if `item` is not a mapping specifying a file 'path' and,
        optionally, a 'title', or is not a string (specifying a file path).
        """
        try:
            return (item.get('title'), item['path'])
        except (AttributeError, TypeError):
            if not isinstance(item, str):
                return None
            return (None, item)

    @classmethod
    def from_output(cls, output):
        """Return an instance of `cls` if `output` is JSON-encoded test detail.

        Return None if `output` is not a JSON-encoded object or does not contain
        test detail (as understood by this class).
        """
        required = {'result', 'reason'}
        try:
            obj = json.loads(output)
            if frozenset(obj.keys()).intersection(required) != required:
                return None
        except (TypeError, json.JSONDecodeError, AttributeError):
            return None
        images = []
        for item in obj.get('plot', ()):
            try:
                (title, path) = cls._image_item(item)
            except ValueError:
                return None
            images.append((title, path))
        tables = []
        dct = obj.get('analysis')
        if dct is not None:
            if not isinstance(dct, dict):
                return None
            analysis = {}
            for (key, val) in dct.items():
                if isinstance(val, dict):
                    tables.append((key, val))
                elif isinstance(val, list):
                    try:
                        analysis[key] = '\n'.join(val)
                    except TypeError:
                        return None
                else:
                    analysis[key] = val
            if analysis:
                tables.insert(0, ('analysis', analysis))
        return cls(images, tables)


class TestSuite(OrderedDict):
    """A test suite with sequence order of test cases preserved."""

    def __init__(self, elem):
        super().__init__()
        self._name = elem.get('name')
        self._metadata = self._metadata_from_elem(elem)
        for child in elem.findall('testcase'):
            case = TestCase(child)
            if case.name in self:
                raise KeyError(f'duplicate test case "{case.name}"')
            self[case.name] = case

    @staticmethod
    def _metadata_from_elem(elem):
        """Return a dict of test suite metadata from `elem`."""
        tests = int(elem.get('tests'))
        errors = int(elem.get('errors'))
        failures = int(elem.get('failures'))
        time = elem.get('time')
        return {
            'tests': tests,
            'errors': errors,
            'failures': failures,
            'success': tests - (errors + failures),
            'skipped': int(elem.get('skipped')),
            'hostname': elem.get('hostname'),
            'timestamp': elem.get('timestamp'),
            'duration': Decimal(time) if time is not None else time,
        }

    @property
    def name(self):
        """The name of this test suite."""
        return self._name

    def summary(self):
        """Generate asciidoc summary for this test suite."""
        yield ''
        yield '[cols="1,3"]'
        yield '|==='
        yield ''
        yield row('*hostname*', self._metadata['hostname'] or NOT_RECORDED)
        yield row('*started*', self._metadata['timestamp'] or NOT_RECORDED)
        yield row('*duration (s)*', self._metadata['duration'])
        yield row('*test cases*', self._metadata['tests'])
        yield row('*test error*', self._metadata['errors'])
        yield row('*test failure*', self._metadata['failures'])
        yield row('*test success*', self._metadata['success'])
        yield ''
        yield '|==='
        yield ''
        yield '[%header,cols="5,1"]'
        yield '|==='
        yield '|case|result'
        yield from (row(c.xref_result, c.a_result) for c in self.values())
        yield '|==='

    def results(self, objdir, config, level):
        """Generate asciidoc results for this test suite."""
        for case in self.values():
            yield ''
            yield case.anchor_result
            yield f'{level} {config.case_title(case)}'
            yield ''
            yield '[cols="1,4"]'
            yield '|==='
            yield ''
            yield row('*test specification*', case.xref_spec)
            yield row('*test identifier*', pdf_test_identifier_cell(case))
            yield row('*timestamp*', case.timestamp or NOT_RECORDED)
            duration = NOT_RECORDED if case.duration is None else case.duration
            yield row('*duration (s)*', duration)
            yield row('*result*', case.a_result)
            yield row('*reason*', case.reason or EMPTY)
            yield '|==='
            detail = TestDetail.from_output(case.stdout)
            if detail:
                yield from detail.to_asciidoc(objdir)
            elif case.stdout:
                yield literal_block(case.stdout)
            yield ''
            yield '<<<'

    def specs(self, objdir, config, level):
        """Generate asciidoc test specs for this test suite."""
        for case in self.values():
            path = config.case_path_testspec(case)
            yield ''
            yield case.anchor_spec
            if path:
                filename = f'{case.uuid}.adoc'
                target = os.path.join(objdir, filename)
                copyfile(path, target)
                indent_titles(target, level)
                yield f'include::{filename}[]'
            else:
                yield f'_(No test specification for {config.case_title(case)})_'
            yield ''
            yield '<<<'


class TestSuites(OrderedDict):
    """Test suites with sequence order of inclusion preserved."""

    def include(self, filename):
        """Include test suites from JUnit XML in `filename`."""
        root = ET.parse(filename).getroot()
        for elem in root.findall('testsuite'):
            suite = TestSuite(elem)
            if suite.name in self:
                raise KeyError(f'duplicate test suite "{suite.name}"')
            self[suite.name] = suite

    def summary(self, level):
        """Generate asciidoc summary in test suite order."""
        for suite in self.values():
            yield ''
            yield f'{level} Test Suite: {suite.name}'
            yield from suite.summary()
            yield ''
            yield '<<<'

    def results(self, objdir, config, level):
        """Generate asciidoc results in test suite order."""
        for suite in self.values():
            yield ''
            yield f'{level} Test Suite: {suite.name}'
            yield from suite.results(objdir, config, level + '=')
            yield ''
            yield '<<<'

    def specs(self, objdir, config, level):
        """Generate asciidoc test specifications in test suite order."""
        for suite in self.values():
            yield ''
            yield f'{level} Test Suite: {suite.name}'
            yield from suite.specs(objdir, config, level + '=')
            yield ''
            yield '<<<'


def main():
    """Generate asciidoc from JUnit XML files.

    Each input file must conform to XML Schema `junit/schema/testdrive.xsd`.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        'objdir',
        help=' '.join((
            "target directory to copy included asciidoc and image files to;",
            "copying image files assumes that images/ subdirectory exists",
        ))
    )
    aparser.add_argument(
        'config',
        help=' '.join((
            "a file containing config as a JSON object with:",
            "the value at 'repositories' mapping repository name to local path",
            "(a local path under which testspec.adoc files can be found); and",
            "the value at 'suites' mapping suite name to an object which maps",
            "'repository' to a repository name (per 'repositories') and",
            "'baseurl' to the base URL for this suite's test identifiers",
            "(the test identifier for a test is expected in the property for",
            "'test_id' in JUnit; the relative path for this id under 'baseurl'",
            "gives the relative path into the repository for testspec.adoc)",
        )),
    )
    aparser.add_argument(
        'input', nargs='*',
        help="input files, or '-' to read from stdin",
    )
    args = aparser.parse_args()
    objdir = args.objdir
    config = Config.json(args.config)
    suites = TestSuites()
    for input_ in args.input:
        suites.include(input_)
    level_suite = '==='
    print('')
    print('== Summary')
    print(*suites.summary(level_suite), sep='\n')
    print('')
    print('== Test Results')
    print(*suites.results(objdir, config, level_suite), sep='\n')
    print('')
    print('[appendix]')
    print('== Test Specifications')
    print(*suites.specs(objdir, config, level_suite), sep='\n')


if __name__ == '__main__':
    main()
