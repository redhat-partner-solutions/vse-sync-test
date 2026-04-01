# Message Interval Test Plan

Test plan for verifying PTP message intervals on T-BC/T-TSC devices, using TCP dumps as reference for expected behavior and validation.

---

## Reference: 230126_E830TT_TBC1.pcap

**File**: `230126_E830TT_TBC1.pcap` (E830TT T-BC Class 1 capture)

This pcap serves as the reference capture for message interval characterization.

### Observed Message Intervals (from tcpdump analysis)

| Message Type | log_message_interval | Interpreted Value | Interval | Actual (measured) |
|--------------|---------------------|------------------|----------|-------------------|
| Sync         | 252                 | -4 (signed)      | 2⁻⁴ s   | ~62.5 ms          |
| Follow_Up    | 252                 | -4 (signed)      | 2⁻⁴ s   | ~62.5 ms          |
| Announce     | 253                 | -3 (signed)      | 2⁻³ s   | ~125 ms           |

*IEEE 1588 logMessageInterval is an 8-bit signed integer: interval = 2^logMessageInterval seconds*

### Pcap Characteristics

- **Domain**: 24 (ITU-T full timing support)
- **Mode**: Two-step (Flags [two step])
- **Clock identity**: 0xc4d6d3fffe58d06c
- **Message sequence**: Announce → Sync → Follow_Up → Sync → Follow_Up → … (announce every 2 sync periods)
- **Capture start**: 19:17:55.079916 (announce), 19:17:55.141566 (first sync)

---

## Goal

Verify that the SUT (T-BC or T-TSC) transmits PTP Sync, Follow_Up, and Announce messages at the intervals advertised in the `log_message_interval` field of each message, within tolerance.

---

## Scope

- Verify **Sync** message interval
- Verify **Follow_Up** message interval (relative to preceding Sync)
- Verify **Announce** message interval
- Support validation against reference capture (e.g., 230126_E830TT_TBC1.pcap)
- Applicable to G.8273.2 T-BC/T-TSC Class-C (and related profiles)

---

## Out of Scope

- Independent validation of the test environment
- Validation of timestamp accuracy (covered by time-error tests)
- Delay_Req / Delay_Resp interval (peer-to-peer or E2E) unless explicitly added later

---

## Prerequisites

### Tools

- `tcpdump` (with PTP dissector)
- `tshark` (optional, for richer analysis)
- Access to capture on the PTP port of the SUT

### Environment

- Promiscuous capture on the link carrying PTP traffic from the SUT
- Stable, locked PTP state before capture start

---

## Test Cases

### TC-1: Sync Message Interval

**Objective**: Verify Sync messages are sent at the interval specified by `log_message_interval` (Sync/Sync_Receive).

**Procedure**:

1. Configure SUT for locked PTP operation (e.g., G.8273.2 Class-C profile).
2. Start capture on the PTP port:
   ```bash
   tcpdump -i <iface> -w sync_interval_capture.pcap -U port 319 or port 320
   ```
3. Capture for at least 60 seconds (prefer 300 s for statistical confidence).
4. Filter Sync messages (exclude Follow_Up):
   ```bash
   tcpdump -r sync_interval_capture.pcap -nn 2>/dev/null | grep "msg type : sync msg" | grep -v "follow up"
   ```
5. Extract timestamps and compute inter-packet intervals.
6. Compare to expected interval from `log_message_interval` (e.g., 252 → 1/16 s).

**Acceptance criteria**:

- Mean Sync interval is within ±5% of 2^logMessageInterval seconds.
- No long gaps > 2× the nominal interval (except during state transitions).
- `log_message_interval` in Sync messages is consistent (e.g., 252 for 1/16 s).

---

### TC-2: Follow_Up Message Interval (vs Sync)

**Objective**: Verify each Sync is followed by a Follow_Up within a short, bounded delay.

**Procedure**:

1. Use the same capture as TC-1.
2. Filter Sync and Follow_Up by sequence ID; measure Sync→Follow_Up delay.
   ```bash
   tcpdump -r sync_interval_capture.pcap -nn 2>/dev/null | grep -E "sync msg|follow up msg"
   ```
3. Compute Sync-to-Follow_Up latency per sequence.

**Acceptance criteria**:

- Follow_Up follows the corresponding Sync within < 10 ms (typical).
- Follow_Up `log_message_interval` matches Sync.

---

### TC-3: Announce Message Interval

**Objective**: Verify Announce messages are sent at the interval specified by `log_message_interval` (Announce).

**Procedure**:

1. Use the same capture as TC-1.
2. Filter Announce messages:
   ```bash
   tcpdump -r sync_interval_capture.pcap -nn 2>/dev/null | grep "msg type : announce msg"
   ```
3. Compute inter-Announce intervals.
4. Compare to 2^logMessageInterval (e.g., 253 → 1/8 s).

**Acceptance criteria**:

- Mean Announce interval is within ±5% of 2^logMessageInterval seconds.
- `log_message_interval` in Announce is consistent (e.g., 253 for 1/8 s).

---

### TC-4: Comparison with Reference Capture

**Objective**: Use the reference pcap (230126_E830TT_TBC1.pcap) to validate analysis scripts and acceptance thresholds.

**Procedure**:

1. Run the interval analysis on `230126_E830TT_TBC1.pcap`:
   ```bash
   tcpdump -r /path/to/230126_E830TT_TBC1.pcap -nn 2>/dev/null | grep "msg type : sync msg" | grep -v "follow up" > sync_only.txt
   ```
2. Compute Sync intervals from sync_only.txt timestamps.
3. Verify expected values:
   - Sync interval: ~62.5 ms (log 252 = -4)
   - Announce interval: ~125 ms (log 253 = -3)

**Reference values** (from 230126_E830TT_TBC1.pcap):

| Metric              | Expected | Typical Range   |
|---------------------|----------|-----------------|
| Sync interval       | 62.5 ms  | 62–63 ms        |
| Announce interval   | 125 ms   | 124–126 ms      |
| Sync→Follow_Up gap  | < 1 ms   | ~0.3–0.5 ms     |

---

## Analysis Script Hints

### Extract Sync Timestamps (bash)

```bash
tcpdump -r capture.pcap -nn 2>/dev/null | grep "msg type : sync msg" | grep -v "follow up" | awk '{print $1, $2}'
```

### Compute Intervals (Python example)

```python
# Parse tcpdump output timestamps (HH:MM:SS.microseconds)
# Convert to seconds, compute deltas, compare to 2^log_interval
```

### log_message_interval Decoding

- Stored as 8-bit signed in PTP header.
- 252 (unsigned) = -4 (signed) → 2^(-4) = 1/16 s = 62.5 ms.
- 253 (unsigned) = -3 (signed) → 2^(-3) = 1/8 s = 125 ms.

---

## References

- IEEE 1588-2019: Precision Time Protocol
- ITU-T G.8273.2: Timing characteristics of telecom boundary clocks and telecom time slave clocks
- Reference pcap: `230126_E830TT_TBC1.pcap`

---

## Test Execution Checklist

- [ ] Prerequisites: tcpdump available, capture permissions
- [ ] SUT in locked PTP state before capture
- [ ] Capture duration ≥ 60 s (prefer 300 s)
- [ ] TC-1: Sync interval within ±5% of nominal
- [ ] TC-2: Follow_Up follows Sync within 10 ms
- [ ] TC-3: Announce interval within ±5% of nominal
- [ ] TC-4: Reference pcap analysis matches expected values
