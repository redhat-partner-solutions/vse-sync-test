### SPDX-License-Identifier: GPL-2.0-or-later

"""Generate JUnit output"""

from argparse import ArgumentParser
import json

from xml.etree import ElementTree as ET

from ..cases import summarize
from ..common import open_input
from ..uri import UriBuilder


def _buildattrs(**kwargs):
    """Return a dict from `kwargs` suitable for creating an XML element with."""
    attrs = {}
    for key, val in kwargs.items():
        if val is not None:
            attrs[key] = str(val)
    return attrs


def _testsuites(
    tests,
    errors,
    failures,
    skipped=0,
    time=None,
):
    """Return XML testsuites element, root element.

    `tests` is the number of tests run;
    `errors` the number of tests which did not return a result;
    `failures` the number of tests which returned a failure result;
    `skipped` the number of tests not run;
    `time` the elapsed time to run all tests.
    """
    attrs = _buildattrs(
        tests=tests,
        errors=errors,
        failures=failures,
        skipped=skipped,
        time=time,
    )
    return ET.Element("testsuites", attrs)


def _testsuite(
    suite,
    tests,
    errors,
    failures,
    skipped=0,
    hostname=None,
    timestamp=None,
    time=None,
):  # pylint: disable=too-many-arguments
    """Return XML testsuite element, a container for test cases.

    `suite` is the name of the test suite;
    `tests` is the number of tests run;
    `errors` the number of tests which did not return a result;
    `failures` the number of tests which returned a failure result;
    `skipped` the number of tests not run;
    `hostname` the name of the host which ran the tests;
    `timestamp` the ISO 8601 datetime when the suite was run;
    `time` the elapsed time to run all tests.
    """
    attrs = _buildattrs(
        name=suite,
        tests=tests,
        errors=errors,
        failures=failures,
        skipped=skipped,
        hostname=hostname,
        timestamp=timestamp,
        time=time,
    )
    return ET.Element("testsuite", attrs)


def _testcase(
    suite,
    case,
    time=None,
):
    """Return XML testcase element.

    `suite` is the name of the test suite;
    `case` is the name of the test case;
    `time` the elapsed time to run the test.
    """
    attrs = _buildattrs(
        classname=suite,
        name=case,
        time=time,
    )
    return ET.Element("testcase", attrs)


def _error(message):
    """Return XML error element.

    `message` is the error reason. (Only the first line will be included.)
    """
    attrs = _buildattrs(
        type="Error",
        message=message.split("\n", 1)[0],
    )
    return ET.Element("error", attrs)


def _failure(message):
    """Return XML failure element.

    `message` is the failure reason. (Only the first line will be included.)
    """
    attrs = _buildattrs(
        type="Failure",
        message=message.split("\n", 1)[0],
    )
    return ET.Element("failure", attrs)


def _system_out(case, exclude=()):
    """Return XML system-out element.

    Include `case` as a pretty-printed JSON-encoded object,
    having omitted pairs for keys in `exclude`.
    """
    elem = ET.Element("system-out")
    elem.text = json.dumps(
        {k: v for (k, v) in case.items() if k not in exclude},
        sort_keys=True,
        indent=4,
    )
    return elem


def _properties(*args):
    """Return XML properties element.

    Include a sub-element for each property (name, value) in `args`.
    """
    elem = ET.Element("properties")
    for name, value in args:
        elem.append(ET.Element("property", name=name, value=str(value)))
    return elem


def junit(
    suite,
    cases,
    hostname=None,
    exclude=(),
    baseurl_ids=None,
    baseurl_specs=None,
    prettify=False,
):
    """Return JUnit output for test `cases` in `suite`.

    `suite` is the string name of the test suite;
    `cases` is a sequence of dict, with each dict defining test case result and
    metadata;
    `hostname` the name of the host which ran the tests;
    `exclude` is a sequence of keys to omit from the JSON object in system-out;
    `baseurl_ids` is the base URL for test ids;
    `baseurl_specs` is the base URL for test specifications;
    if `prettify` then indent XML output.

    Each case must supply values for keys:
        id - the test URI
        result - a boolean test result or "error" (no result produced)
        reason - string reason describing test failure or error

    Each case may supply values for keys:
        timestamp - ISO 8601 string of UTC time when the test was started
        duration - test duration in seconds

    If `timestamp` is supplied then `duration` must also be supplied.

    If both `baseurl_ids` and `baseurl_specs` are supplied then add a property
    element for 'test_specification' for each case. The element text is a URL
    formed by substituting `baseurl_specs` for the base (prefix) of the case
    'id' (which must be `baseurl_ids`).
    """
    uri_builder = None
    # always ensure base URLs are valid
    if baseurl_ids:
        UriBuilder(baseurl_ids)
    if baseurl_specs:
        UriBuilder(baseurl_specs)
    # only use base URLs if both are supplied
    if baseurl_ids and baseurl_specs:
        uri_builder = UriBuilder(baseurl_ids)
    summary = summarize(cases)
    tests = summary["total"]
    errors = summary["error"]
    failures = summary["failure"]
    timestamp = summary["timestamp"]
    time_total = summary["duration"]
    e_root = _testsuites(tests, errors, failures)
    e_suite = _testsuite(
        suite,
        tests,
        errors,
        failures,
        hostname=hostname,
        timestamp=timestamp,
        time=time_total,
    )
    for case in cases:
        e_case = _testcase(suite, case["id"], time=case.get("duration"))
        if case["result"] is False:
            e_case.append(_failure(case["reason"]))
        elif case["result"] == "error":
            e_case.append(_error(case["reason"]))
        elif case["result"] is not True:
            raise ValueError(f"""bad result "{case['result']}" for case {case['id']}""")
        e_case.append(_system_out(case, exclude=exclude))
        properties = [("test_id", case["id"])]
        if uri_builder:
            testspec_url = uri_builder.rebase(case["id"], baseurl_specs)
            properties.append(("test_specification", testspec_url))
        e_case.append(_properties(*properties))
        e_suite.append(e_case)
    e_root.append(e_suite)
    if prettify:
        ET.indent(e_root)
    return ET.tostring(e_root, encoding="unicode", xml_declaration=True)


def main():
    """Generate JUnit output for test cases.

    Build JUnit output for the test cases in input. Print the JUnit output to
    stdout. Each line of input must contain a JSON object specifying the test
    id, result and other metadata for a single test case.
    """
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        "--hostname",
        help=" ".join(
            (
                "The name of the host which ran the tests.",
                "(Used in JUnit output when supplied.)",
            )
        ),
    )
    aparser.add_argument(
        "--exclude",
        nargs="*",
        default=("id",),
        help="Omit pairs for these keys from the JSON object in <system-out>",
    )
    aparser.add_argument(
        "--prettify",
        action="store_true",
        help="pretty print XML output",
    )
    aparser.add_argument(
        "--baseurl-ids",
        help="The base URL which test ids are relative to.",
    )
    aparser.add_argument(
        "--baseurl-specs",
        help="The base URL which test specifications are relative to.",
    )
    aparser.add_argument(
        "suite",
        help="The name of the test suite. (Used in JUnit output.)",
    )
    aparser.add_argument(
        "input",
        help="input file, or '-' to read from stdin",
    )
    args = aparser.parse_args()
    with open_input(args.input) as fid:
        cases = tuple(json.loads(line) for line in fid)
    print(
        junit(
            args.suite,
            cases,
            args.hostname,
            args.exclude,
            args.baseurl_ids,
            args.baseurl_specs,
            args.prettify,
        )
    )


if __name__ == "__main__":
    main()
