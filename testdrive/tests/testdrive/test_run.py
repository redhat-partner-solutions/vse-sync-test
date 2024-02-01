### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for testdrive.run"""

import os.path

from unittest import TestCase

from testdrive.run import drive

EXAMPLES = os.path.join(
    os.path.dirname(__file__),
    "../../examples/",
)


class TestDrive(TestCase):
    """Tests for testdrive.run.drive"""

    def test_success(self):
        """Test testdrive.run.drive with test success"""
        test = os.path.join(EXAMPLES, "sequence/B/testimpl.py")
        self.assertEqual(
            drive(test),
            {"argv": (), "result": True, "reason": None, "data": {"baz": 99}},
        )

    def test_failure(self):
        """Test testdrive.run.drive with test failure"""
        test = os.path.join(EXAMPLES, "sequence/C/test.sh")
        self.assertEqual(
            drive(test),
            {"argv": (), "result": False, "reason": "no particular reason"},
        )

    def test_error(self):
        """Test testdrive.run.drive with test error"""
        test = os.path.join(EXAMPLES, "terror.sh")
        self.assertEqual(
            drive(test),
            {
                "argv": (),
                "result": "error",
                "reason": f"{test} exited with code 7\n\nfoo\nbaz\n",
            },
        )
