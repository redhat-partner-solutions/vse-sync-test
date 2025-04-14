### SPDX-License-Identifier: GPL-2.0-or-later

"""Analyze ts2phc log messages"""
from .analyzer import TimeErrorAnalyzerBase
from .analyzer import TimeDeviationAnalyzerBase
from .analyzer import MaxTimeIntervalErrorAnalyzerBase


class TimeErrorAnalyzer(TimeErrorAnalyzerBase):
    """Analyze time error"""
    id_ = 'ts2phc/time-error'
    parser = id_
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class TimeDeviationAnalyzer(TimeDeviationAnalyzerBase):
    """Analyze time deviation"""
    id_ = 'ts2phc/time-deviation'
    parser = 'ts2phc/time-error'
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class MaxTimeIntervalErrorAnalyzer(MaxTimeIntervalErrorAnalyzerBase):
    """Analyze max time interval error"""
    id_ = 'ts2phc/mtie'
    parser = 'ts2phc/time-error'
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))
