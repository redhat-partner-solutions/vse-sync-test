### SPDX-License-Identifier: GPL-2.0-or-later

"""Generate JUnit output"""

from argparse import ArgumentParser
import json
from urllib.parse import parse_qs

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
    base_stripped = baseurl_ids.rstrip("/") if baseurl_ids else ""

    def _strip_path_prefix(path):
        """Remove sync/G.8272/ and sync/G.8273.2/ from path for shorter display."""
        for prefix in ("sync/G.8272/", "sync/G.8273.2/"):
            if path.startswith(prefix):
                return path[len(prefix):]
        return path

    # Human-readable test descriptions for PDF (test identifier and test case name)
    # Keys are path prefixes (metric/segment); match longest prefix first
    _TEST_DESCRIPTIONS = (
        (
            "time-error-in-locked-mode/1PPS-to-DPLL",
            "Verify time error on path of 1PPS input to 1PPS output of DPLL in locked condition",
        ),
        ("time-error-in-locked-mode/DPLL-to-PHC", "Verify time error on path of DPLL to PHC in locked condition"),
        ("time-error-in-locked-mode/SMA1-to-DPLL", "Verify time error on path of SMA1 to DPLL in locked condition"),
        (
            "time-error-in-locked-mode/Constellation-to-GNSS-receiver",
            "Verify time error on path of constellation to GNSS receiver in locked condition",
        ),
        (
            "time-error-in-locked-mode/PHC-to-SYS",
            "Verify time error on path of PHC to system clock in locked condition",
        ),
        ("time-error-in-locked-mode/PTP4L-to-PHC", "Verify time error on path of PTP4L to PHC in locked condition"),
        (
            "time-error-in-locked-mode/system-test-PHC-to-SYS",
            "Verify time error on path of PHC to system clock in locked condition (system test)",
        ),
        (
            "wander-TDEV-in-locked-mode/1PPS-to-DPLL",
            "Verify TDEV (Time Deviation in locked mode) on path of 1PPS input to "
            "1PPS output of DPLL in locked condition",
        ),
        (
            "wander-TDEV-in-locked-mode/DPLL-to-PHC",
            "Verify TDEV (Time Deviation in locked mode) on path of DPLL to PHC in locked condition",
        ),
        (
            "wander-TDEV-in-locked-mode/SMA1-to-DPLL",
            "Verify TDEV (Time Deviation in locked mode) on path of SMA1 to DPLL in locked condition",
        ),
        (
            "wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver",
            "Verify TDEV (Time Deviation in locked mode) on path of constellation to "
            "GNSS receiver in locked condition",
        ),
        (
            "wander-TDEV-in-locked-mode/system-test-PHC-to-SYS",
            "Verify TDEV (Time Deviation in locked mode) on path of PHC to system clock "
            "in locked condition (system test)",
        ),
        (
            "wander-MTIE-in-locked-mode/1PPS-to-DPLL",
            "Verify MTIE (Maximum Time Interval Error) on path of 1PPS input to 1PPS "
            "output of DPLL in locked condition",
        ),
        (
            "wander-MTIE-in-locked-mode/DPLL-to-PHC",
            "Verify MTIE (Maximum Time Interval Error) on path of DPLL to PHC in locked condition",
        ),
        (
            "wander-MTIE-in-locked-mode/SMA1-to-DPLL",
            "Verify MTIE (Maximum Time Interval Error) on path of SMA1 to DPLL in locked condition",
        ),
        (
            "wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver",
            "Verify MTIE (Maximum Time Interval Error) on path of constellation to GNSS "
            "receiver in locked condition",
        ),
        (
            "wander-MTIE-in-locked-mode/system-test-PHC-to-SYS",
            "Verify MTIE (Maximum Time Interval Error) on path of PHC to system clock in "
            "locked condition (system test)",
        ),
        (
            "TDEV-in-locked-mode/1PPS-to-DPLL",
            "Verify TDEV (Time Deviation in locked mode) on path of 1PPS input to 1PPS "
            "output of DPLL in locked condition",
        ),
        (
            "TDEV-in-locked-mode/DPLL-to-PHC",
            "Verify TDEV (Time Deviation in locked mode) on path of DPLL to PHC in locked condition",
        ),
        (
            "TDEV-in-locked-mode/SMA1-to-DPLL",
            "Verify TDEV (Time Deviation in locked mode) on path of SMA1 to DPLL in locked condition",
        ),
        (
            "TDEV-in-locked-mode/PTP4L-to-PHC",
            "Verify TDEV (Time Deviation in locked mode) on path of PTP4L to PHC in locked condition",
        ),
        (
            "MTIE-for-LPF-filtered-series/1PPS-to-DPLL",
            "Verify MTIE (Maximum Time Interval Error) on path of 1PPS input to 1PPS output "
            "of DPLL in locked condition",
        ),
        (
            "MTIE-for-LPF-filtered-series/DPLL-to-PHC",
            "Verify MTIE (Maximum Time Interval Error) on path of DPLL to PHC in locked condition",
        ),
        (
            "MTIE-for-LPF-filtered-series/SMA1-to-DPLL",
            "Verify MTIE (Maximum Time Interval Error) on path of SMA1 to DPLL in locked condition",
        ),
        (
            "MTIE-for-LPF-filtered-series/PTP4L-to-PHC",
            "Verify MTIE (Maximum Time Interval Error) on path of PTP4L to PHC in locked condition",
        ),
        ("phc/state-transitions", "Verify PHC state transitions"),
        ("ptp-workload", "Verify clock accuracy under PTP workload"),
    )

    def _path_to_description(path):
        """Return human-readable description for path, or None if no match."""
        # Match longest prefix first
        for prefix, desc in sorted(_TEST_DESCRIPTIONS, key=lambda x: -len(x[0])):
            if path.startswith(prefix):
                return desc
        return None

    # Build interface name -> card-N mapping (ens3f0->card-1, ens3f1->card-2, etc.)
    _unique_names = set()
    for case in cases:
        cid = case.get("id", "")
        if "?" in cid:
            _, query_part = cid.split("?", 1)
            params = parse_qs(query_part)
            if "name" in params:
                _unique_names.update(params["name"])
    _name_to_card = {n: f"card-{i + 1}" for i, n in enumerate(sorted(_unique_names))}

    def _display_name(case_id):
        """Use human-readable description for PDF when available, else path-based name.
        Always append variant (PRTC-A, PRTC-B, Class-C, RAN) and card [card-N] when present."""
        if base_stripped and case_id.startswith(base_stripped):
            path_part, _, query_part = case_id[len(base_stripped):].lstrip("/").partition("?")
            path = path_part.rstrip("/")
            path = _strip_path_prefix(path)
            # Extract variant (PRTC-A, PRTC-B, Class-C, RAN) and card - keep in name
            segments = path.split("/")
            raw_variant = segments[-1] if segments and segments[-1] in ("PRTC-A", "PRTC-B", "Class-C", "RAN") else ""
            variant_expand = {
                "PRTC-A": "PRTC-A (Higher accuracy (e.g. for GNSS-based primary references))",
                "PRTC-B": "PRTC-B (Lower accuracy (e.g. for holdover or less precise references))",
            }
            variant = variant_expand.get(raw_variant, raw_variant)
            desc = _path_to_description(path)
            if desc is not None:
                if "MTIE" in desc and "Maximum Time Interval Error" in desc:
                    result = f"{desc} {variant} with a 0.1 Hz low-pass filter".strip()
                else:
                    result = f"{desc} {variant}".strip() if variant else desc
            else:
                result = path
            if query_part:
                params = parse_qs(query_part)
                if "name" in params and params["name"]:
                    iface = params["name"][0]
                    card = _name_to_card.get(iface, iface)
                    result = f"{result} [{card}]"
            return result
        return case_id

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
        display_name = _display_name(case["id"]) if baseurl_ids else case["id"]
        e_case = _testcase(suite, display_name, time=case.get("duration"))
        if case["result"] is False:
            e_case.append(_failure(case["reason"]))
        elif case["result"] == "error":
            e_case.append(_error(case["reason"]))
        elif case["result"] is not True:
            raise ValueError(f"""bad result "{case['result']}" for case {case['id']}""")
        e_case.append(_system_out(case, exclude=exclude))
        properties = [("test_id", display_name)]
        if uri_builder:
            testspec_url = uri_builder.rebase(case["id"], baseurl_specs)
            properties.append(("test_specification", testspec_url))
        # GitHub tree URL for the test case directory (PDF: clickable test identifier)
        if baseurl_ids and case.get("id"):
            properties.append(("test_directory_url", case["id"].split("?", 1)[0]))
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
