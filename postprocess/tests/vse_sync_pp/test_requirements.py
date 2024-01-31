### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.requirements"""

### ensure values in REQUIREMENTS have to be changed in two places

from unittest import TestCase

from vse_sync_pp.requirements import REQUIREMENTS


class TestRequirements(TestCase):
    """Test cases for vse_sync_pp.requirements.REQUIREMENTS"""
    def test_g8272_prtc_a(self):
        """Test G.8272/PRTC-A requirement values"""

        self.assertEqual(REQUIREMENTS['G.8272/PRTC-A']['time-error-in-locked-mode/ns'], 100)

        (interval1, func1), (interval2, func2) = REQUIREMENTS['G.8272/PRTC-A']['maximum-time-interval-error-in-locked-mode/ns'].items() # noqa

        self.assertEqual(func1(100), 52.5)
        self.assertEqual(func2(300), 100)

        (interval1, func1), (interval2, func2), (interval3, func3) = REQUIREMENTS['G.8272/PRTC-A']['time-deviation-in-locked-mode/ns'].items() # noqa
        self.assertEqual(func1(100), 3)
        self.assertEqual(func2(150), 4.5)
        self.assertEqual(func3(550), 30)

    def test_g8272_prtc_b(self):
        """Test G.8272/PRTC-B requirement values"""

        self.assertEqual(REQUIREMENTS['G.8272/PRTC-B']['time-error-in-locked-mode/ns'], 40)

        (interval1, func1), (interval2, func2) = REQUIREMENTS['G.8272/PRTC-B']['maximum-time-interval-error-in-locked-mode/ns'].items() # noqa

        self.assertEqual(func1(100), 52.5)
        self.assertEqual(func2(300), 40)

        (interval1, func1), (interval2, func2), (interval3, func3) = REQUIREMENTS['G.8272/PRTC-B']['time-deviation-in-locked-mode/ns'].items() # noqa
        self.assertEqual(func1(100), 1)
        self.assertEqual(func2(150), 1.5)
        self.assertEqual(func3(550), 5)

    def test_workload_RAN(self):
        """Test workload/RAN requirement values"""
        self.assertEqual(REQUIREMENTS['workload/RAN']['time-error-in-locked-mode/ns'], 100)
