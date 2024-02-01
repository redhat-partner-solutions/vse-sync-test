### SPDX-License-Identifier: GPL-2.0-or-later

"""Run tests"""

import json
from argparse import ArgumentParser
import sys
import os
import subprocess
from datetime import datetime, timezone

from .common import open_input, print_line
from .source import Source, sequence
from .uri import UriBuilder


def drive(test, *test_args):
    """Execute `test` and return a result dict.

    If `test` exits with error or outputs to stderr, then the result dict
    will contain string 'error' at key 'result' and a string at key 'reason'.

    Otherwise the result dict contains whatever `test` outputs to stdout. This
    output is always expected to be a JSON object with pairs for 'result',
    'reason' and other pairs appropriate for `test`.

    The result dict always contains `test_args` at key 'argv'.
    """
    subp = subprocess.run(
        (test,) + test_args,
        capture_output=True,
        check=False,
        env=os.environ,
    )
    if not subp.returncode and not subp.stderr:
        dct = json.loads(subp.stdout)
    else:
        reason = f"{test} exited with code {subp.returncode}"
        if subp.stderr:
            reason += "\n\n"
            reason += subp.stderr.decode()
            dct = {"result": "error", "reason": reason}
    dct["argv"] = test_args
    return dct


def plot(plotter, prefix, *test_args):
    """Execute `plotter` and return a sequence of images output.

    If `plotter` exits with error or outputs to stderr, then raise RuntimeError.

    Otherwise the sequence of images output contains whatever `plotter` outputs
    to stdout. This output is always expected to be a JSON array whose items are
    either a string, the path to an image filename, or an object with pairs for
    'path', the path to an image filename, and optionally a string 'title'. Each
    image output by `plotter` is expected to use `prefix` as the path and stem
    for the output filename.
    """
    subp = subprocess.run(
        (plotter, prefix) + test_args,
        capture_output=True,
        check=False,
        env=os.environ,
    )
    if not subp.returncode and not subp.stderr:
        return json.loads(subp.stdout)
    reason = f"{plotter} exited with code {subp.returncode}:"
    reason += "\n\n"
    reason += subp.stderr.decode()
    raise RuntimeError(reason)


def timenow():
    """Return a datetime value for UTC time now."""
    return datetime.now(timezone.utc)


def timestamp(dtv):
    """Return an ISO 8601 string for datetime value `dtv`."""
    return datetime.isoformat(dtv)


def timevalue(string):
    """Return a datetime value for ISO 8601 `string`."""
    return datetime.fromisoformat(string)


def main():
    """Run tests"""
    aparser = ArgumentParser(description=main.__doc__)
    aparser.add_argument(
        "--basedir",
        help=" ".join(
            (
                "The base directory which tests are relative to.",
                "If not supplied tests are relative to directory of `input`.",
            )
        ),
    )
    aparser.add_argument(
        "--imagedir",
        help=" ".join(
            (
                "The directory which plot image files are to be generated in.",
                "If not supplied then no plots are generated.",
            )
        ),
    )
    aparser.add_argument(
        "--plotter",
        default="plot.py",
        help=" ".join(
            (
                "Generate a plot of test data by calling a script with this name.",
                "The script must be colocated with the test implementation.",
                "The args to the script are the output filename, followed by the",
                "same argv as passed to the test implementation.",
                "Ignored if plots are not generated.",
            )
        ),
    )
    aparser.add_argument(
        "baseurl",
        help="The base URL which test ids are relative to.",
    )
    aparser.add_argument(
        "input",
        help=" ".join(
            (
                "File containing tests to run or '-' to read from stdin.",
                "Each test is specified on a separate line as a JSON array.",
                "The first element is the name of the test implementation,",
                "relative to `--basedir`.",
                "The remaining elements are args to the test implementation.",
            )
        ),
    )
    args = aparser.parse_args()
    basedir = args.basedir or os.path.dirname(args.input)
    builder = UriBuilder(args.baseurl)
    with open_input(args.input) as fid:
        source = Source(sequence(json.loads(line) for line in fid))
        for test, *test_args in source.next():
            id_ = builder.build(os.path.dirname(test))
            testimpl = os.path.join(basedir, test)
            start = timenow()
            result = drive(testimpl, *test_args)
            end = timenow()
            result["id"] = id_
            if "timestamp" not in result:
                result["timestamp"] = timestamp(start)
                result["duration"] = (end - start).total_seconds()
            if result["result"] in (True, False) and args.imagedir:
                plotter = os.path.join(os.path.dirname(testimpl), args.plotter)
                if os.path.isfile(plotter):
                    prefix = os.path.join(
                        args.imagedir,
                        os.path.splitext(test)[0].strip("/").replace("/", "_"),
                    )
                    result["plot"] = plot(plotter, prefix, *test_args)
            # Python exits with error code 1 on EPIPE
            if not print_line(json.dumps(result)):
                sys.exit(1)


if __name__ == "__main__":
    main()
