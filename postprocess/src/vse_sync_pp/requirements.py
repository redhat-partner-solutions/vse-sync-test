### SPDX-License-Identifier: GPL-2.0-or-later

"""Requirements specified in ITU-T G.8272/Y.1367"""

REQUIREMENTS = {
    'G.8272/PRTC-A': {
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 273): lambda t: 0.275 * t + 25,
            (274, 100000): lambda t: 100
        },
        'time-deviation-in-locked-mode/ns': {
            (None, 100): lambda t: 3,
            (101, 1000): lambda t: 0.03 * t,
            (1001, 100000): lambda t: 30
        },
        'time-error-in-locked-mode/ns': 100,
    },
    'G.8272/PRTC-B': {
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 54.5): lambda t: 0.275 * t + 25,
            (54.5, 100000): lambda t: 40
        },
        'time-deviation-in-locked-mode/ns': {
            (None, 100): lambda t: 1,
            (101, 500): lambda t: 0.01 * t,
            (501, 100000): lambda t: 5
        },
        'time-error-in-locked-mode/ns': 40,
    },
    'workload/RAN': {
        'time-error-in-locked-mode/ns': 100,
        'time-deviation-in-locked-mode/ns': {
            (None, 1000000): lambda t: 100
        },
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 100000): lambda t: 1
        }
    },
    'G.8273.2/Class-A': {
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 40): lambda t: 22 * t + 1.121,
            (40, 1000): lambda t: 40
        },
        'time-deviation-in-locked-mode/ns': {
            (None, 1000): lambda t: 4,
            (10, 1000): lambda t: 0.04 * t,
            (40, 1000): lambda t: 40
        },
        'time-error-in-locked-mode/ns': 100,
    },
    'G.8273.2/Class-B': {
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 1000): lambda t: 22 * t + 1.257,
            (40, 10000): lambda t: 40
        },
        'time-deviation-in-locked-mode/ns': {
            (None, 1000): lambda t: 4,
            (10, 1000): lambda t: 0.04 * t,
            (40, 1000): lambda t: 40
        },
        'time-error-in-locked-mode/ns': 40,
    },
    'G.8273.2/Class-C': {
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 1000): lambda t: 10,
        },
        'time-deviation-in-locked-mode/ns': {
            (None, 1000): lambda t: 20,
        },
        'time-error-in-locked-mode/ns': 20,
    },
    'workload/RAN': {
        'time-error-in-locked-mode/ns': 100,
        'time-deviation-in-locked-mode/ns': {
            (None, 1000): lambda t: 10
        },
        'maximum-time-interval-error-in-locked-mode/ns': {
            (None, 10000): lambda t: 10
        }
    },
}
