### SPDX-License-Identifier: GPL-2.0-or-later

"""Analyze ptp4l log messages"""
from .analyzer import TimeErrorAnalyzerBase
from .analyzer import TimeDeviationAnalyzerBase
from .analyzer import MaxTimeIntervalErrorAnalyzerBase


class TimeErrorAnalyzer(TimeErrorAnalyzerBase):
    """Analyze time error for ptp4l boundary clock"""
    id_ = 'ptp4l/time-error'
    parser = id_
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class TimeDeviationAnalyzer(TimeDeviationAnalyzerBase):
    """Analyze time deviation for ptp4l boundary clock"""
    id_ = 'ptp4l/time-deviation'
    parser = 'ptp4l/time-error'
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))


class MaxTimeIntervalErrorAnalyzer(MaxTimeIntervalErrorAnalyzerBase):
    """Analyze max time interval error for ptp4l boundary clock"""
    id_ = 'ptp4l/mtie'
    parser = 'ptp4l/time-error'
    locked = frozenset({'s2', 's3'})

    def test(self, data):
        return self._check_missing_samples(data, *super().test(data))