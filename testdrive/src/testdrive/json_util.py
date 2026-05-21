### SPDX-License-Identifier: GPL-2.0-or-later

"""JSON helpers for test results containing Decimal/numpy values."""

import json
from decimal import Decimal

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


class TestResultEncoder(json.JSONEncoder):
    """Encode test output objects for testdrive and JUnit."""

    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if np is not None:
            if isinstance(o, np.ndarray):
                return o.tolist()
            if isinstance(o, np.generic):
                return o.item()
        return super().default(o)


def dumps(obj, **kwargs):
    """Return JSON text for a test result or analysis object."""
    kwargs.setdefault("cls", TestResultEncoder)
    return json.dumps(obj, **kwargs)
