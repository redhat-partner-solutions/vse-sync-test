### SPDX-License-Identifier: GPL-2.0-or-later

"""Common test functions"""


def make_fqname(subject):
    """Return the fully-qualified name of test `subject`."""
    # subject is assumed to be a class
    return '.'.join((
        subject.__module__,
        subject.__name__,
    ))
