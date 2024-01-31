### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.analyzers.pmc"""

from unittest import TestCase
from collections import namedtuple
from decimal import Decimal

from vse_sync_pp.analyzers.pmc import ClockStateAnalyzer

from .test_analyzer import AnalyzerTestBuilder

CLOCK_CLASS = namedtuple('CLOCK_CLASS', ('timestamp', 'clock_class', 'clockAccuracy', 'offsetScaledLogVariance'))


class TestClockStateAnalyzer(TestCase, metaclass=AnalyzerTestBuilder):
    """Test cases for vse_sync_pp.analyzers.pmc.ClockStateAnalyzer"""
    constructor = ClockStateAnalyzer
    id_ = 'phc/gm-settings'
    parser = 'phc/gm-settings'
    expect = (
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (),
            'result': "error",
            'reason': "no data",
            'timestamp': None,
            'duration': None,
            'analysis': {},
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal('0'), 248, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal('1'), 12, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "wrong clock class 12",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 7, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 1,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 140, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 1,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 150, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 1,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 160, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 1
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 6, '0x21', '0x4E5D'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 6, '0x21', '0x4E5D'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 140, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 1,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 6, '0x21', '0x4E5D'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 150, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 1,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 6, '0x21', '0x4E5D'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 160, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 1
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 7, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 140, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 150, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 160, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 140, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 7, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 1,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 150, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 7, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 1,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 160, '0xFE', '0xFFFF'),
                # wrong state transition
                CLOCK_CLASS(Decimal(1), 7, '0xFE', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal state transition",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 1,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 1
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                # wrong clock accuracy
                CLOCK_CLASS(Decimal(1), 248, '0x21', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal clock accuracy",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 7, '0xFE', '0xFFFF'),
                # wrong clock accuracy
                CLOCK_CLASS(Decimal(1), 7, '0x21', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal clock accuracy",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 1,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 140, '0xFE', '0xFFFF'),
                # wrong clock accuracy
                CLOCK_CLASS(Decimal(1), 140, '0x21', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal clock accuracy",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 1,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 150, '0xFE', '0xFFFF'),
                # wrong clock accuracy
                CLOCK_CLASS(Decimal(1), 150, '0x21', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal clock accuracy",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 1,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 160, '0xFE', '0xFFFF'),
                # wrong clock accuracy
                CLOCK_CLASS(Decimal(1), 160, '0x21', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal clock accuracy",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 1
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 6, '0x21', '0x4E5D'),
                # wrong clock accuracy
                CLOCK_CLASS(Decimal(1), 6, '0xFE', '0x4E5D'),
            ),
            'result': False,
            'reason': "illegal clock accuracy",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 1,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 6, '0x21', '0x4E5D'),
                # wrong offset scaled log variance
                CLOCK_CLASS(Decimal(1), 6, '0x21', '0xFFFF'),
            ),
            'result': False,
            'reason': "illegal offset scaled log variance",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 1,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                # wrong offset scaled log variance
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0x4E5D'),
            ),
            'result': False,
            'reason': "illegal offset scaled log variance",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 7, '0xFE', '0xFFFF'),
                # wrong offset scaled log variance
                CLOCK_CLASS(Decimal(1), 7, '0xFE', '0x4E5D'),
            ),
            'result': False,
            'reason': "illegal offset scaled log variance",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 1,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 140, '0xFE', '0xFFFF'),
                # wrong offset scaled log variance
                CLOCK_CLASS(Decimal(1), 140, '0xFE', '0x4E5D'),
            ),
            'result': False,
            'reason': "illegal offset scaled log variance",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 1,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 150, '0xFE', '0xFFFF'),
                # wrong offset scaled log variance
                CLOCK_CLASS(Decimal(1), 150, '0xFE', '0x4E5D'),
            ),
            'result': False,
            'reason': "illegal offset scaled log variance",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 1,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 160, '0xFE', '0xFFFF'),
                # wrong offset scaled log variance
                CLOCK_CLASS(Decimal(1), 160, '0xFE', '0x4E5D'),
            ),
            'result': False,
            'reason': "illegal offset scaled log variance",
            'timestamp': Decimal(0),
            'duration': Decimal(1),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 0,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 1
                        }
                    }
                },
                "total_transitions": 0
            }
        },
        {
            'requirements': 'G.8272/PRTC-B',
            'parameters': {
                'min-test-duration/s': 1,
            },
            'rows': (
                CLOCK_CLASS(Decimal(0), 248, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(1), 248, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(2), 6, '0x21', '0x4E5D'),
                CLOCK_CLASS(Decimal(3), 7, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(4), 140, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(5), 6, '0x21', '0x4E5D'),
                CLOCK_CLASS(Decimal(6), 7, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(7), 150, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(8), 6, '0x21', '0x4E5D'),
                CLOCK_CLASS(Decimal(9), 7, '0xFE', '0xFFFF'),
                CLOCK_CLASS(Decimal(10), 160, '0xFE', '0xFFFF'),
            ),
            'result': True,
            'reason': None,
            'timestamp': Decimal(0),
            'duration': Decimal(10),
            'analysis': {
                "clock_class_count": {
                    "FREERUN": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 1,
                            "LOCKED": 1,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "LOCKED": {
                        "count": 3,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 3,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_IN_SPEC": {
                        "count": 3,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 1,
                            "HOLDOVER_OUT_SPEC2": 1,
                            "HOLDOVER_OUT_SPEC3": 1
                        }
                    },
                    "HOLDOVER_OUT_SPEC1": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 1,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC2": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 1,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    },
                    "HOLDOVER_OUT_SPEC3": {
                        "count": 1,
                        "transitions": {
                            "FREERUN": 0,
                            "LOCKED": 0,
                            "HOLDOVER_IN_SPEC": 0,
                            "HOLDOVER_OUT_SPEC1": 0,
                            "HOLDOVER_OUT_SPEC2": 0,
                            "HOLDOVER_OUT_SPEC3": 0
                        }
                    }
                },
                "total_transitions": 9
            }
        },
    )
