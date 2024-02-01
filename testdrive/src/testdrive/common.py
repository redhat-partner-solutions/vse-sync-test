### SPDX-License-Identifier: GPL-2.0-or-later

"""Common code for command line tools"""

import sys
from contextlib import nullcontext


def open_input(filename, encoding="utf-8", **kwargs):
    """Return a context manager for reading from `filename`.

    If `filename` is '-' then read from stdin instead of `filename`.
    """
    if filename == "-":
        return nullcontext(sys.stdin)
    return open(filename, encoding=encoding, **kwargs)


def print_line(line, flush=True):
    """Print `line` and, optionally, `flush` stdout.

    If SIGPIPE is received then set `sys.stdout` to None and return False:
    otherwise return True.

    The Python recommendation suggests this clean up on SIGPIPE:
    https://docs.python.org/3/library/signal.html#note-on-sigpipe

    However this code uses setting `sys.stdout` to None as per:
    https://stackoverflow.com/questions/26692284/\
    how-to-prevent-brokenpipeerror-when-doing-a-flush-in-python
    """
    try:
        print(line, flush=flush)
        return True
    except BrokenPipeError:
        sys.stdout = None
        return False
