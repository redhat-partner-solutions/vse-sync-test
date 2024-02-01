### SPDX-License-Identifier: GPL-2.0-or-later

"""Test sources"""


def sequence(*args):
    """A generator of a linear sequence of tests from `args`."""
    yield from args


class Source:
    """A source of tests to run."""

    def __init__(self, generator):
        self._generator = generator

    def next(self):
        """Return the next test to run, or None."""
        try:
            return next(self._generator)
        except StopIteration:
            return None
