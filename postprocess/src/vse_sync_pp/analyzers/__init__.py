### SPDX-License-Identifier: GPL-2.0-or-later

"""Analyzers"""

from .analyzer import Config # noqa

from . import (
    gnss,
    ppsdpll,
    ts2phc,
    phc2sys,
    pmc,
    ptp4l,
)

ANALYZERS = {
    cls.id_: cls for cls in (
        gnss.TimeErrorAnalyzer,
        ppsdpll.TimeErrorAnalyzer,
        ts2phc.TimeErrorAnalyzer,
        phc2sys.TimeErrorAnalyzer,
        pmc.ClockStateAnalyzer,
        ptp4l.TimeErrorAnalyzer,
        gnss.TimeDeviationAnalyzer,
        ppsdpll.TimeDeviationAnalyzer,
        ts2phc.TimeDeviationAnalyzer,
        phc2sys.TimeDeviationAnalyzer,
        ptp4l.TimeDeviationAnalyzer,
        gnss.MaxTimeIntervalErrorAnalyzer,
        ppsdpll.MaxTimeIntervalErrorAnalyzer,
        ts2phc.MaxTimeIntervalErrorAnalyzer,
        phc2sys.MaxTimeIntervalErrorAnalyzer,
        ptp4l.MaxTimeIntervalErrorAnalyzer,
    )
}
