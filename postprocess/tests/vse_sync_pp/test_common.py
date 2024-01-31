### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.common"""

import json
from decimal import Decimal

from unittest import TestCase

from vse_sync_pp.common import JsonEncoder


class TestJsonEncoder(TestCase):
    """Test cases for vse_sync_pp.common.JsonEncoder"""
    def test_success(self):
        """Test vse_sync_pp.common.JsonEncoder encodes Decimal"""
        self.assertEqual(
            json.dumps(Decimal('123.456'), cls=JsonEncoder),
            '123.456',
        )

    def test_error(self):
        """Test vse_sync_pp.common.JsonEncoder rejects instance"""
        with self.assertRaises(TypeError):
            json.dumps(self, cls=JsonEncoder)
