### SPDX-License-Identifier: GPL-2.0-or-later

"""Analyze PMC log messages"""

from .analyzer import Analyzer
import copy

STATE_FREERUN = 248
STATE_LOCKED = 6
STATE_HOLDOVER_IN_SPEC = 7
STATE_HOLDOVER_OUT_OF_SPEC1 = 140
STATE_HOLDOVER_OUT_OF_SPEC2 = 150
STATE_HOLDOVER_OUT_OF_SPEC3 = 160
CLOCK_ACCURACY_NANO_SECONDS100 = "0x27"
CLOCK_ACCURACY_UNKNOWN = "0xFE"
OFFSET_SCALED_LOG_VARIANCE_CONNECTED = "0x4E5D"
OFFSET_SCALED_LOG_VARIANCE_NOT_CONNECTED = "0xFFFF"

STATE_NAMES = {
    STATE_FREERUN: "FREERUN",
    STATE_LOCKED: "LOCKED",
    STATE_HOLDOVER_IN_SPEC: "HOLDOVER_IN_SPEC",
    STATE_HOLDOVER_OUT_OF_SPEC1: "HOLDOVER_OUT_SPEC1",
    STATE_HOLDOVER_OUT_OF_SPEC2: "HOLDOVER_OUT_SPEC2",
    STATE_HOLDOVER_OUT_OF_SPEC3: "HOLDOVER_OUT_SPEC3",
}

STATE_TRANSITION = {
    STATE_FREERUN: [STATE_FREERUN, STATE_LOCKED],
    STATE_LOCKED: [STATE_LOCKED, STATE_HOLDOVER_IN_SPEC],
    STATE_HOLDOVER_IN_SPEC: [STATE_LOCKED,
                             STATE_HOLDOVER_IN_SPEC,
                             STATE_HOLDOVER_OUT_OF_SPEC1,
                             STATE_HOLDOVER_OUT_OF_SPEC2,
                             STATE_HOLDOVER_OUT_OF_SPEC3],
    STATE_HOLDOVER_OUT_OF_SPEC1: [STATE_LOCKED,
                                  STATE_HOLDOVER_OUT_OF_SPEC1,
                                  STATE_HOLDOVER_OUT_OF_SPEC2,
                                  STATE_HOLDOVER_OUT_OF_SPEC3],
    STATE_HOLDOVER_OUT_OF_SPEC2: [STATE_LOCKED,
                                  STATE_HOLDOVER_OUT_OF_SPEC1,
                                  STATE_HOLDOVER_OUT_OF_SPEC2,
                                  STATE_HOLDOVER_OUT_OF_SPEC3],
    STATE_HOLDOVER_OUT_OF_SPEC3: [STATE_LOCKED,
                                  STATE_HOLDOVER_OUT_OF_SPEC1,
                                  STATE_HOLDOVER_OUT_OF_SPEC2,
                                  STATE_HOLDOVER_OUT_OF_SPEC3],
}

BASE_CLOCK_CLASS_COUNT = {
    "count": 0,
    "transitions": {
        STATE_FREERUN: 0,
        STATE_LOCKED: 0,
        STATE_HOLDOVER_IN_SPEC: 0,
        STATE_HOLDOVER_OUT_OF_SPEC1: 0,
        STATE_HOLDOVER_OUT_OF_SPEC2: 0,
        STATE_HOLDOVER_OUT_OF_SPEC3: 0,
    },
}

CLOCK_ACCURACY_FOR_CLOCK_CLASS = {
    STATE_FREERUN: CLOCK_ACCURACY_UNKNOWN,
    STATE_LOCKED: CLOCK_ACCURACY_NANO_SECONDS100,
    STATE_HOLDOVER_IN_SPEC: CLOCK_ACCURACY_UNKNOWN,
    STATE_HOLDOVER_OUT_OF_SPEC1: CLOCK_ACCURACY_UNKNOWN,
    STATE_HOLDOVER_OUT_OF_SPEC2: CLOCK_ACCURACY_UNKNOWN,
    STATE_HOLDOVER_OUT_OF_SPEC3: CLOCK_ACCURACY_UNKNOWN,
}

OFFSET_SCALED_LOG_VARIANCE_FOR_CLOCK_CLASS = {
    STATE_FREERUN: OFFSET_SCALED_LOG_VARIANCE_NOT_CONNECTED,
    STATE_LOCKED: OFFSET_SCALED_LOG_VARIANCE_CONNECTED,
    STATE_HOLDOVER_IN_SPEC: OFFSET_SCALED_LOG_VARIANCE_NOT_CONNECTED,
    STATE_HOLDOVER_OUT_OF_SPEC1: OFFSET_SCALED_LOG_VARIANCE_NOT_CONNECTED,
    STATE_HOLDOVER_OUT_OF_SPEC2: OFFSET_SCALED_LOG_VARIANCE_NOT_CONNECTED,
    STATE_HOLDOVER_OUT_OF_SPEC3: OFFSET_SCALED_LOG_VARIANCE_NOT_CONNECTED,
}


def is_illegal_transition(current_state, new_state):
    return new_state not in STATE_TRANSITION[current_state]


def is_illegal_clock_accuracy(state, clock_accuracy):
    return clock_accuracy.upper() != CLOCK_ACCURACY_FOR_CLOCK_CLASS[state].upper()


def is_illegal_offset_scaled_log_variance(state, offset_scaled_log_variance):
    return offset_scaled_log_variance.upper() != OFFSET_SCALED_LOG_VARIANCE_FOR_CLOCK_CLASS[state].upper()


def get_named_clock_class_result(clock_class_count):
    named_clock_class_count = {STATE_NAMES[k]: v for (k, v) in clock_class_count.items()}
    for clock_class in clock_class_count.values():
        clock_class["transitions"] = {STATE_NAMES[k]: v for (k, v) in clock_class["transitions"].items()}
    return named_clock_class_count


class ClockStateAnalyzer(Analyzer):
    """Analyze clock state
    """
    id_ = 'phc/gm-settings'
    parser = id_

    def __init__(self, config):
        super().__init__(config)
        # minimum test duration for a valid test
        self._duration_min = config.parameter('min-test-duration/s')
        self.transition_count = 0
        self.clock_class_count = {
            STATE_FREERUN: copy.deepcopy(BASE_CLOCK_CLASS_COUNT),
            STATE_LOCKED: copy.deepcopy(BASE_CLOCK_CLASS_COUNT),
            STATE_HOLDOVER_IN_SPEC: copy.deepcopy(BASE_CLOCK_CLASS_COUNT),
            STATE_HOLDOVER_OUT_OF_SPEC1: copy.deepcopy(BASE_CLOCK_CLASS_COUNT),
            STATE_HOLDOVER_OUT_OF_SPEC2: copy.deepcopy(BASE_CLOCK_CLASS_COUNT),
            STATE_HOLDOVER_OUT_OF_SPEC3: copy.deepcopy(BASE_CLOCK_CLASS_COUNT),
        }

    def prepare(self, rows):
        idx = 0
        try:
            tstart = rows[0].timestamp
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

        if data.iloc[-1].timestamp - data.iloc[0].timestamp < self._duration_min:
            return (False, "short test duration")
        if len(data) - 1 < self._duration_min:
            return (False, "short test samples")

        state = None
        illegal_transition = False
        illegal_clock_accuracy = False
        illegal_offset_scaled_log_variance = False
        for index, row in data.iterrows():
            clock_class = row['clock_class']
            clock_accuracy = row['clockAccuracy']
            offset_scaled_log_variance = row['offsetScaledLogVariance']

            if (state is None) and (clock_class in STATE_TRANSITION):
                state = clock_class
            else:
                if clock_class != state:
                    self.transition_count += 1

                if clock_class not in STATE_TRANSITION:
                    return (False, f"wrong clock class {clock_class}")

                if is_illegal_transition(state, clock_class):
                    illegal_transition = True

                self.clock_class_count[state]["transitions"][clock_class] += 1
                state = clock_class
                self.clock_class_count[clock_class]["count"] += 1

                if is_illegal_clock_accuracy(state, clock_accuracy):
                    illegal_clock_accuracy = True
                if is_illegal_offset_scaled_log_variance(state, offset_scaled_log_variance):
                    illegal_offset_scaled_log_variance = True
        if illegal_transition:
            return (False, "illegal state transition")
        if illegal_clock_accuracy:
            return (False, "illegal clock accuracy")
        if illegal_offset_scaled_log_variance:
            return (False, "illegal offset scaled log variance")
        return (True, None)

    def explain(self, data):
        if len(data) == 0:
            return {}

        return {
            'timestamp': self._timestamp_from_dec(data.iloc[0].timestamp),
            'duration': data.iloc[-1].timestamp - data.iloc[0].timestamp,
            'clock_class_count': get_named_clock_class_result(self.clock_class_count),
            'total_transitions': self.transition_count,
        }
