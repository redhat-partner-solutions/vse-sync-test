### SPDX-License-Identifier: GPL-2.0-or-later

"""Analyze phc2sys log messages"""

from .analyzer import TimeErrorAnalyzerBase
from .analyzer import TimeDeviationAnalyzerBase
from .analyzer import MaxTimeIntervalErrorAnalyzerBase


class TimeErrorAnalyzer(TimeErrorAnalyzerBase):
    """Analyze time error"""
    id_ = 'phc2sys/time-error'
    parser = id_
    locked = frozenset({'s2'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class TimeDeviationAnalyzer(TimeDeviationAnalyzerBase):
    """Analyze time deviation"""
    id_ = 'phc2sys/time-deviation'
    parser = 'phc2sys/time-error'
    locked = frozenset({'s2'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class MaxTimeIntervalErrorAnalyzer(MaxTimeIntervalErrorAnalyzerBase):
    """Analyze max time interval error"""
    id_ = 'phc2sys/mtie'
    parser = 'phc2sys/time-error'
    locked = frozenset({'s2'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))
