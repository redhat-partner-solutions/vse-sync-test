### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for vse_sync_pp.parsers.ptp4l"""

from unittest import TestCase
from decimal import Decimal

from vse_sync_pp.parsers.ptp4l import (
    TimeErrorParser,
    PortStateParser,
)

from .test_parser import ParserTestBuilder


class TestTimeErrorParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.ptp4l.TimeErrorParser"""

    constructor = TimeErrorParser
    id_ = "ptp4l/time-error"
    elems = ("timestamp", "interface", "terror", "state", "freq", "path_delay")
    accept = (
        (
            "ptp4l[681011.839]: [ptp4l.0.config] "
            "eth3 master offset -23947 s0 freq +0 path delay 11350",
            (Decimal("681011.839"), "eth3", -23947, "s0", 0, 11350),
        ),
        (
            "ptp4l[681012.840]: [ptp4l.1.config] "
            "enp2s0f0 master offset -4552 s2 freq -30035 path delay 10385",
            (Decimal("681012.840"), "enp2s0f0", -4552, "s2", -30035, 10385),
        ),
        (
            "ptp4l[681013.841]: "
            "eth0 master offset 1150 s1 freq +25000 path delay 8500",
            (Decimal("681013.841"), "eth0", 1150, "s1", 25000, 8500),
        ),
        (
            "ptp4l[681014.842]: "
            "/dev/ptp0 master offset -500 s2 freq -5000 path delay 12000",
            (Decimal("681014.842"), "/dev/ptp0", -500, "s2", -5000, 12000),
        ),
    )
    reject = (
        # Missing master offset
        "ptp4l[681011.839]: eth3 freq +0 path delay 11350",
        # Wrong format
        "ts2phc[681011.839]: eth3 master offset -23947 s0 freq +0",
        # Missing path delay
        "ptp4l[681011.839]: eth3 master offset -23947 s0 freq +0",
        # Invalid timestamp
        "ptp4l[invalid]: eth3 master offset -23947 s0 freq +0 path delay 11350",
    )


class TestTimeErrorParserWithInterface(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.ptp4l.TimeErrorParser with specific interface"""

    constructor = lambda: TimeErrorParser(interface="eth3")
    id_ = "ptp4l/time-error"
    elems = ("timestamp", "interface", "terror", "state", "freq", "path_delay")
    accept = (
        (
            "ptp4l[681011.839]: [ptp4l.0.config] "
            "eth3 master offset -23947 s0 freq +0 path delay 11350",
            (Decimal("681011.839"), "eth3", -23947, "s0", 0, 11350),
        ),
        (
            "ptp4l[681012.840]: "
            "eth3 master offset -4552 s2 freq -30035 path delay 10385",
            (Decimal("681012.840"), "eth3", -4552, "s2", -30035, 10385),
        ),
    )
    reject = (
        # Different interface should be rejected
        "ptp4l[681011.839]: eth0 master offset -23947 s0 freq +0 path delay 11350",
        "ptp4l[681011.839]: enp2s0f0 master offset -23947 s0 freq +0 path delay 11350",
    )


class TestPortStateParser(TestCase, metaclass=ParserTestBuilder):
    """Test cases for vse_sync_pp.parsers.ptp4l.PortStateParser"""

    constructor = PortStateParser
    id_ = "ptp4l/port-state"
    elems = ("timestamp", "port", "from_state", "to_state", "event")
    accept = (
        (
            "ptp4l[681011.839]: [ptp4l.0.config] "
            "port 1: INITIALIZING to LISTENING on INIT_COMPLETE",
            (Decimal("681011.839"), 1, "INITIALIZING", "LISTENING", "INIT_COMPLETE"),
        ),
        (
            "ptp4l[681012.840]: "
            "port 1: LISTENING to UNCALIBRATED on RS_SLAVE",
            (Decimal("681012.840"), 1, "LISTENING", "UNCALIBRATED", "RS_SLAVE"),
        ),
        (
            "ptp4l[681013.841]: "
            "port 1: UNCALIBRATED to SLAVE on MASTER_CLOCK_SELECTED",
            (Decimal("681013.841"), 1, "UNCALIBRATED", "SLAVE", "MASTER_CLOCK_SELECTED"),
        ),
        (
            "ptp4l[681014.842]: "
            "port 2: LISTENING to MASTER on ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES",
            (Decimal("681014.842"), 2, "LISTENING", "MASTER", "ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES"),
        ),
    )
    reject = (
        # Missing port number
        "ptp4l[681011.839]: INITIALIZING to LISTENING on INIT_COMPLETE",
        # Wrong format
        "ts2phc[681011.839]: port 1: INITIALIZING to LISTENING on INIT_COMPLETE",
        # Missing event
        "ptp4l[681011.839]: port 1: INITIALIZING to LISTENING",
        # Invalid timestamp
        "ptp4l[invalid]: port 1: INITIALIZING to LISTENING on INIT_COMPLETE",
    ) 