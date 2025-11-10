# PTP4L Parser for Boundary Clock

This document describes the new ptp4l parser that has been added to handle boundary clock functionality, similar to how the ts2phc parser handles grandmaster functionality.

## Overview

The ptp4l parser provides two main parser classes:

1. **TimeErrorParser** - Parses time error information from ptp4l log messages
2. **PortStateParser** - Parses port state transitions to monitor boundary clock behavior

## Usage

### TimeErrorParser

Parses log lines containing master offset, servo state, frequency adjustment, and path delay information:

```python
from vse_sync_pp.parsers.ptp4l import TimeErrorParser

parser = TimeErrorParser()
line = "ptp4l[681011.839]: eth3 master offset -23947 s0 freq +0 path delay 11350"
result = parser.parse_line(line)
# Result: Parsed(timestamp=Decimal('681011.839'), interface='eth3', terror=-23947, 
#                state='s0', freq=0, path_delay=11350)
```

You can also specify a specific interface to filter for:

```python
parser = TimeErrorParser(interface="eth3")
# Will only parse lines for eth3 interface
```

### PortStateParser

Parses port state transitions to monitor PTP clock behavior:

```python
from vse_sync_pp.parsers.ptp4l import PortStateParser

parser = PortStateParser()
line = "ptp4l[681011.839]: port 1: INITIALIZING to LISTENING on INIT_COMPLETE"
result = parser.parse_line(line)
# Result: Parsed(timestamp=Decimal('681011.839'), port=1, from_state='INITIALIZING', 
#                to_state='LISTENING', event='INIT_COMPLETE')
```

## Analyzers

The ptp4l parser also includes corresponding analyzer classes:

### TimeErrorAnalyzer, TimeDeviationAnalyzer, MaxTimeIntervalErrorAnalyzer

These work similarly to the ts2phc analyzers but for ptp4l boundary clock data.

### PortStateAnalyzer

Analyzes port state transitions to determine if the system is operating as:
- **Boundary Clock**: Has both slave and master ports
- **Ordinary Clock (Slave)**: Has only slave ports 
- **Ordinary Clock (Master)**: Has only master ports

```python
from vse_sync_pp.analyzers.ptp4l import PortStateAnalyzer

analyzer = PortStateAnalyzer()
result, message = analyzer.test(port_state_data)
# Returns (True, "Boundary Clock operating correctly: Slave ports [1], Master ports [2]")
```

## Log Format Examples

The parser handles various ptp4l log formats:

**Time Error Messages:**
```
ptp4l[681011.839]: [ptp4l.0.config] eth3 master offset -23947 s0 freq +0 path delay 11350
ptp4l[681012.840]: enp2s0f0 master offset -4552 s2 freq -30035 path delay 10385
ptp4l[681013.841]: /dev/ptp0 master offset 1150 s1 freq +25000 path delay 8500
```

**Port State Transitions:**
```
ptp4l[681011.839]: port 1: INITIALIZING to LISTENING on INIT_COMPLETE
ptp4l[681012.840]: port 1: LISTENING to UNCALIBRATED on RS_SLAVE
ptp4l[681013.841]: port 1: UNCALIBRATED to SLAVE on MASTER_CLOCK_SELECTED
ptp4l[681014.842]: port 2: LISTENING to MASTER on ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES
```

## Integration

The parser classes are automatically registered in the PARSERS and ANALYZERS dictionaries and can be used with the existing vse_sync_pp framework for analyzing PTP boundary clock performance.

## Comparison with ts2phc Parser

| Feature | ts2phc Parser | ptp4l Parser |
|---------|---------------|--------------|
| Purpose | Parse GM sync messages | Parse BC sync messages |
| Time Error | ✓ | ✓ |
| Interface Support | ✓ | ✓ |
| State Monitoring | Clock servo states | Port states + servo states |
| BC-Specific | ✗ | ✓ Port state analysis |
| Config File Support | ✓ | ✓ |

The ptp4l parser provides similar functionality to ts2phc but specifically handles boundary clock scenarios where you need to monitor both slave and master port behavior. 