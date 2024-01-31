### SPDX-License-Identifier: GPL-2.0-or-later

"""Common analyzer functionality"""

import yaml
from pandas import DataFrame
from datetime import (datetime, timezone)

import allantools
import numpy as np

from scipy import signal as scipy_signal

from ..requirements import REQUIREMENTS


class Config():
    """Analyzer configuration"""
    def __init__(self, filename=None, requirements=None, parameters=None):
        self._filename = filename
        self._requirements = requirements
        self._parameters = parameters

    def _reason(self, reason):
        """Return `reason`, extended if this config is from a file."""
        if self._filename is None:
            return reason
        return reason + f' in config file {self._filename}'

    def requirement(self, key):
        """Return the value at `key` in this configuration's requirements.

        Raise :class:`KeyError` if a value cannot be returned.
        """
        try:
            return REQUIREMENTS[self._requirements][key]
        except KeyError as exc:
            if self._requirements is None:
                reason = 'no requirements specified'
            elif self._requirements not in REQUIREMENTS:
                reason = f'unknown requirements {self._requirements}'
            else:
                reason = f'unknown requirement {key} in {self._requirements}'
            raise KeyError(self._reason(reason)) from exc

    def parameter(self, key):
        """Return the value at `key` in this configuration's parameters.

        Raise :class:`KeyError` if a value cannot be returned.
        """
        try:
            return self._parameters[key]
        except TypeError as exc:
            reason = 'no parameters specified'
            raise KeyError(self._reason(reason)) from exc
        except KeyError as exc:
            reason = f'unknown parameter {key}'
            raise KeyError(self._reason(reason)) from exc

    @classmethod
    def from_yaml(cls, filename, encoding='utf-8'):
        """Build configuration from YAML file at `filename`"""
        with open(filename, encoding=encoding) as fid:
            dct = dict(yaml.safe_load(fid.read()))
        return cls(filename, dct.get('requirements'), dct.get('parameters'))


class CollectionIsClosed(Exception):
    """Data collection was closed while collecting data"""
    # empty


class Analyzer():
    """A base class providing common analyzer functionality"""
    def __init__(self, config):
        self._config = config
        self._rows = []
        self._data = None
        self._result = None
        self._reason = None
        self._timestamp = None
        self._duration = None
        self._analysis = None

    def collect(self, *rows):
        """Collect data from `rows`"""
        if self._rows is None:
            raise CollectionIsClosed()
        self._rows += rows

    def prepare(self, rows):
        """Return (columns, records) from collected data `rows`

        `columns` is a sequence of column names
        `records` is a sequence of rows prepared for test analysis

        If `records` is an empty sequence, then `columns` is also empty.
        """
        return (rows[0]._fields, rows) if rows else ((), ())

    def close(self):
        """Close data collection"""
        if self._data is None:
            (columns, records) = self.prepare(self._rows)
            self._data = DataFrame.from_records(records, columns=columns)
            self._rows = None

    def _test(self):
        """Close data collection and test collected data"""
        if self._result is None:
            self.close()
            (self._result, self._reason) = self.test(self._data)

    def _explain(self):
        """Close data collection and explain collected data"""
        if self._analysis is None:
            self.close()
            self._analysis = self.explain(self._data)
            self._timestamp = self._analysis.pop('timestamp', None)
            self._duration = self._analysis.pop('duration', None)

    def _timestamp_from_dec(self, dec):
        """Return an absolute timestamp or decimal timestamp from `dec`.

        If `dec` is large enough to represent 2023 (the year this was coded),
        or a later year, then assume it represents an absolute date-time. (This
        is >53 years if counting seconds from zero.) Otherwise assume relative
        time.

        >>> today = datetime.now()
        >>> today
        datetime.datetime(2023, 9, 8, 16, 49, 54, 735285)
        >>> ts = today.timestamp()
        >>> ts
        1694188194.735285
        >>> ts / (365 * 24 * 60 * 60)
        53.72235523640554
        """
        # `dtv` is a timezone-aware datetime value with resolution of seconds
        dtv = datetime.fromtimestamp(int(dec), tz=timezone.utc)
        if datetime.now().year - dtv.year <= 1:
            # absolute date-time
            return dtv.isoformat()
        # relative time
        return dec

    @staticmethod
    def _check_missing_samples(data, result, reason):
        if reason is None:
            if len(data.timestamp.diff().astype(float).round(0).tail(-1).unique()) > 1:
                return (False, "missing test samples")
        return result, reason

    @property
    def result(self):
        """The boolean result from this analyzer's test of the collected data"""
        self._test()
        return self._result

    @property
    def reason(self):
        """A string qualifying :attr:`result` (or None if unqualified)"""
        self._test()
        return self._reason

    @property
    def timestamp(self):
        """The ISO 8601 date-time timestamp, when the test started"""
        self._explain()
        return self._timestamp

    @property
    def duration(self):
        """The test duration in seconds"""
        self._explain()
        return self._duration

    @property
    def analysis(self):
        """A structured analysis of the collected data"""
        self._explain()
        return self._analysis

    @staticmethod
    def _statistics(data, units, ndigits=3):
        """Return a dict of statistics for `data`, rounded to `ndigits`"""
        def _round(val):
            """Return `val` as native Python type or Decimal, rounded to `ndigits`"""
            try:
                return round(val.item(), ndigits)
            except AttributeError:
                return round(val, ndigits)
        min_ = data.min()
        max_ = data.max()
        return {
            'units': units,
            'min': _round(min_),
            'max': _round(max_),
            'range': _round(max_ - min_),
            'mean': _round(data.mean()),
            'stddev': _round(data.std()),
            'variance': _round(data.var()),
        }

    def test(self, data):
        """This analyzer's test of the collected `data`.

        Return a 2-tuple (result, reason) where `result` is a boolean or the
        string "error" and `reason` is a string or None.

        A boolean `result` indicates test success or failure: `result` "error"
        indicates that a result could not be produced.

        A string `reason` qualifies `result`; when None `result` is unqualified.
        """
        raise NotImplementedError

    def explain(self, data):
        """Return a structured analysis of the collected `data`"""
        raise NotImplementedError


class TimeErrorAnalyzerBase(Analyzer):
    """Analyze time error.

    Derived classes must override class attribute `locked`, specifying a
    frozenset of values representing locked states.
    """
    locked = frozenset()

    def __init__(self, config):
        super().__init__(config)
        # required system time output accuracy
        accuracy = config.requirement('time-error-in-locked-mode/ns')
        # limit on inaccuracy at observation point
        limit = config.parameter('time-error-limit/%')
        # exclusive upper bound on absolute time error for any sample
        self._unacceptable = accuracy * (limit / 100)
        # samples in the initial transient period are ignored
        self._transient = config.parameter('transient-period/s')
        # minimum test duration for a valid test
        self._duration_min = config.parameter('min-test-duration/s')

    def prepare(self, rows):
        idx = 0
        try:
            tstart = rows[0].timestamp + self._transient
        except IndexError:
            pass
        else:
            while idx < len(rows):
                if tstart <= rows[idx].timestamp:
                    break
                idx += 1
        return super().prepare(rows[idx:])

    def test(self, data):
        if len(data) == 0:
            return ("error", "no data")
        if frozenset(data.state.unique()).difference(self.locked): # pylint: disable=no-member
            return (False, "loss of lock")
        terr_min = data.terror.min()
        terr_max = data.terror.max()
        if self._unacceptable <= max(abs(terr_min), abs(terr_max)):
            return (False, "unacceptable time error")
        if data.iloc[-1].timestamp - data.iloc[0].timestamp < self._duration_min:
            return (False, "short test duration")
        if len(data) - 1 < self._duration_min:
            return (False, "short test samples")
        return (True, None)

    def explain(self, data):
        if len(data) == 0:
            return {}
        return {
            'timestamp': self._timestamp_from_dec(data.iloc[0].timestamp),
            'duration': data.iloc[-1].timestamp - data.iloc[0].timestamp,
            'terror': self._statistics(data.terror, 'ns'),
        }


def calculate_limit(accuracy, limit_percentage, tau):
    """Calculate upper limit based on tau

    `accuracy` is the list of functions to calculate upper limits
    `limit_percentage` is the unaccuracy percentage
    `tau` is the observation window interval

    Return the upper limit value based on `tau`
    """
    for (low, high), f in accuracy.items():
        if ((low is None or tau > low) and (tau <= high)):
            return f(tau) * (limit_percentage / 100)


def out_of_range(taus, samples, accuracy, limit):
    """Check if the input samples are out of range.

    `taus` list of observation windows intervals
    `samples` are input samples
    `accuracy` contains the list of upper bound limit functions
    `limit` is the percentage to apply the upper limit

    Return `True` if any value in `samples` is out of range
    """
    for tau, sample in zip(taus, samples):
        mask = calculate_limit(accuracy, limit, tau)
        if mask <= sample:
            return True
    return False


def calculate_filter(input_signal, transient, sample_rate):
    """Calculate digital low-pass filter from `input_signal`

    scipy_signal.butter input arguments:
        order of the filter: 1
        critical Frequency in half cycles per sample:
        (for digital filters is normalized from 0 to 1 where 1 is Nyquist frequency)
          cutoff Frequency: 0.1Hz
          sample_rate in samples per second
        btype is band type or type of filter
        analog=False since it is always a digital filter
    scipy_signal.butter return arguments:
        `numerator` coefficient vector and `denominator coefficient vector of the butterworth digital filter
        """
    numerator, denominator = scipy_signal.butter(1, 0.1 / (sample_rate / 2), btype="low", analog=False, output="ba")
    lpf_signal = scipy_signal.filtfilt(numerator, denominator, input_signal.terror)
    lpf_signal = lpf_signal[transient:len(lpf_signal)]
    return lpf_signal


class TimeIntervalErrorAnalyzerBase(Analyzer):
    """Analyze Time Interval Error (also referred to as Wander).

    Derived classes calculate specific Time Interval Error metric focused on measuring
    the change of Time Error.
    """
    locked = frozenset()

    def __init__(self, config):
        super().__init__(config)
        # samples in the initial transient period are ignored
        self._transient = config.parameter('transient-period/s')
        # minimum test duration for a valid test
        self._duration_min = config.parameter('min-test-duration/s')
        # limit initial tau observation windows from 1 to 10k taus
        taus_below_10k = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90,
                                  100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000,
                                  4000, 5000, 6000, 7000, 8000, 9000, 10000])
        # observation window upper limit to 100k samples in 5k increments
        taus_above_10k = np.arange(15000, 100000, 5000)
        # `taus_list` contains range limit of obervation window intervals for which to compute the statistic
        self._taus_list = np.concatenate((taus_below_10k, taus_above_10k))
        self._rate = None
        self._lpf_signal = None

    def prepare(self, rows):
        idx = 0
        try:
            tstart = rows[0].timestamp + self._transient
        except IndexError:
            pass
        else:
            while idx < len(rows):
                if tstart <= rows[idx].timestamp:
                    break
                idx += 1
        return super().prepare(rows[idx:])

    @staticmethod
    def calculate_rate(data):
        # calculate sample rate using 100 samples
        cumdelta = 0

        for i in range(1, 100 if len(data) > 100 else len(data)):
            cumdelta = cumdelta + data.iloc[i].timestamp - data.iloc[i - 1].timestamp
        return round((1 / (cumdelta / 100)))

    def _test_common(self, data):
        if len(data) == 0:
            return ("error", "no data")
        if frozenset(data.state.unique()).difference(self.locked):
            return (False, "loss of lock")
        if data.iloc[-1].timestamp - data.iloc[0].timestamp < self._duration_min:
            return (False, "short test duration")
        if len(data) - 1 < self._duration_min:
            return (False, "short test samples")
        return None

    def _explain_common(self, data):
        if len(data) == 0:
            return {}
        if self._rate is None:
            self._rate = self.calculate_rate(self._data)
        if self._lpf_signal is None:
            self._lpf_signal = calculate_filter(data, self._transient, self._rate)
        return None

    def toplot(self):
        self.close()
        self._generate_taus()
        yield from zip(self._taus, self._samples)

    def _generate_taus(self):
        if self._rate is None:
            self._rate = self.calculate_rate(self._data)
        if self._lpf_signal is None:
            self._lpf_signal = calculate_filter(self._data, self._transient, self._rate)
        return None


class TimeDeviationAnalyzerBase(TimeIntervalErrorAnalyzerBase):
    """Analyze Time Deviation (TDEV).

    Derived classes must override class attribute `locked`, specifying a
    frozenset of values representing locked states.
    """
    def __init__(self, config):
        super().__init__(config)
        # required system time deviation output
        self._accuracy = config.requirement('time-deviation-in-locked-mode/ns')
        # limit of inaccuracy at observation point
        self._limit = config.parameter('time-deviation-limit/%')
        # list of observation windows intervals to calculate TDEV
        # `_taus` is a subset of `taus_list`
        self._taus = None
        # TDEV samples
        self._samples = None

    def _generate_taus(self):
        super()._generate_taus()
        if self._samples is None:
            self._taus, self._samples, errors, ns = allantools.tdev(self._lpf_signal, rate=self._rate, data_type="phase", taus=self._taus_list) # noqa

    def test(self, data):
        result = self._test_common(data)
        if result is None:
            self._generate_taus()
            if out_of_range(self._taus, self._samples, self._accuracy, self._limit):
                return (False, "unacceptable time deviation")
            return (True, None)
        return result

    def explain(self, data):
        analysis = self._explain_common(data)
        if analysis is None:
            self._generate_taus()
            return {
                'timestamp': self._timestamp_from_dec(data.iloc[0].timestamp),
                'duration': data.iloc[-1].timestamp - data.iloc[0].timestamp,
                'tdev': self._statistics(self._samples, 'ns'),
            }
        return analysis


class MaxTimeIntervalErrorAnalyzerBase(TimeIntervalErrorAnalyzerBase):
    """Analyze Maximum Time Interval Error (MTIE).

    Derived classes must override class attribute `locked`, specifying a
    frozenset of values representing locked states.
    """
    def __init__(self, config):
        super().__init__(config)
        # required system maximum time interval error output in ns
        self._accuracy = config.requirement('maximum-time-interval-error-in-locked-mode/ns')
        # limit of inaccuracy at observation point
        self._limit = config.parameter('maximum-time-interval-error-limit/%')
        # list of observation windows intervals to calculate MTIE
        # `_taus` will be a subset of `taus_list`
        self._taus = None
        # MTIE samples
        self._samples = None

    def _generate_taus(self):
        super()._generate_taus()
        if self._samples is None:
            self._taus, self._samples, errors, ns = allantools.mtie(self._lpf_signal, rate=self._rate, data_type="phase", taus=self._taus_list) # noqa

    def test(self, data):
        result = self._test_common(data)
        if result is None:
            self._generate_taus()
            if out_of_range(self._taus, self._samples, self._accuracy, self._limit):
                return (False, "unacceptable mtie")
            return (True, None)
        return result

    def explain(self, data):
        analysis = self._explain_common(data)
        if analysis is None:
            self._generate_taus()
            return {
                'timestamp': self._timestamp_from_dec(data.iloc[0].timestamp),
                'duration': data.iloc[-1].timestamp - data.iloc[0].timestamp,
                'mtie': self._statistics(self._samples, 'ns'),
            }
        return analysis
