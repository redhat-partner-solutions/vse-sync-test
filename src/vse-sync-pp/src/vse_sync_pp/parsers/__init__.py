### SPDX-License-Identifier: GPL-2.0-or-later

"""Parsers"""

from . import dpll
from . import gnss
from . import ts2phc
from . import phc2sys
from . import pmc

PARSERS = {
    cls.id_: cls for cls in (
        dpll.TimeErrorParser,
        gnss.TimeErrorParser,
        ts2phc.TimeErrorParser,
        phc2sys.TimeErrorParser,
        pmc.ClockClassParser,
    )
}
