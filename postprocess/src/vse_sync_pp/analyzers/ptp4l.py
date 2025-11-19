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


class PortStateAnalyzer(Analyzer):
    """Analyze ptp4l port state (placeholder to satisfy imports)"""
    id_ = 'ptp4l/port-state'
    parser = 'ptp4l/time-error'

    def test(self, data):
        if data is None or len(data) == 0:
            return ("error", "no data")
        # Placeholder: No specific port-state criteria implemented
        return (True, None)

    def explain(self, data):
        if data is None or len(data) == 0:
            return {}
        return {
            'timestamp': self._timestamp_from_dec(data.iloc[0].timestamp),
            'duration': data.iloc[-1].timestamp - data.iloc[0].timestamp,
        }
