# Test Case Names: Before vs After (PDF Report)

This document shows how test identifiers and test case names appear in the PDF report before and after the human-readable naming changes.

The **After** column shows the same title as in the PDF; each title is a link to the corresponding test directory on GitHub (`https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/…`).

---

## G.8272 (T-GM Mode) Tests

### Fixed tests (no device params)

| Test Path | Before | After |
|-----------|--------|-------|
| time-error-in-locked-mode/PHC-to-SYS/RAN | `https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/PHC-to-SYS/RAN/` | [Verify time error on path of PHC to system clock in locked condition RAN](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/PHC-to-SYS/RAN/) |
| time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A | `https://github.com/.../sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/` | [Verify time error on path of constellation to GNSS receiver in locked condition PRTC-A (Higher accuracy (e.g. for GNSS-based primary references))](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/) |
| time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B | `https://github.com/.../sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/` | [Verify time error on path of constellation to GNSS receiver in locked condition PRTC-B (Lower accuracy (e.g. for holdover or less precise references))](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/) |
| time-error-in-locked-mode/1PPS-to-DPLL/PRTC-A | `https://github.com/.../sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-A/` | [Verify time error on path of 1PPS input to 1PPS output of DPLL in locked condition PRTC-A (Higher accuracy (e.g. for GNSS-based primary references))](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-A/) |
| time-error-in-locked-mode/1PPS-to-DPLL/PRTC-B | `https://github.com/.../sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-B/` | [Verify time error on path of 1PPS input to 1PPS output of DPLL in locked condition PRTC-B (Lower accuracy (e.g. for holdover or less precise references))](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/1PPS-to-DPLL/PRTC-B/) |
| phc/state-transitions | `https://github.com/.../sync/G.8272/phc/state-transitions/` | [Verify PHC state transitions](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/phc/state-transitions/) |

*wander-TDEV and wander-MTIE variants use the same human-readable pattern with “TDEV (Time Deviation in locked mode)” or “MTIE (Maximum Time Interval Error)” and “with a 0.1 Hz low-pass filter” where applicable.*

### wander-TDEV / wander-MTIE — Constellation-to-GNSS-receiver (G.8272)

| Test Path | Before | After |
|-----------|--------|-------|
| wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B | `.../wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/` | [Verify TDEV (Time Deviation in locked mode) on path of constellation to GNSS receiver in locked condition PRTC-B (Lower accuracy (e.g. for holdover or less precise references))](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/) |
| wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A | `.../wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/` | [Verify TDEV (Time Deviation in locked mode) on path of constellation to GNSS receiver in locked condition PRTC-A (Higher accuracy (e.g. for GNSS-based primary references))](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/wander-TDEV-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/) |
| wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B | `.../wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/` | [Verify MTIE (Maximum Time Interval Error) on path of constellation to GNSS receiver in locked condition PRTC-B (Lower accuracy (e.g. for holdover or less precise references)) with a 0.1 Hz low-pass filter](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-B/) |
| wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A | `.../wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/` | [Verify MTIE (Maximum Time Interval Error) on path of constellation to GNSS receiver in locked condition PRTC-A (Higher accuracy (e.g. for GNSS-based primary references)) with a 0.1 Hz low-pass filter](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/wander-MTIE-in-locked-mode/Constellation-to-GNSS-receiver/PRTC-A/) |

*Same wander-TDEV / wander-MTIE naming pattern for DPLL-to-PHC, SMA1-to-DPLL, and 1PPS-to-DPLL under `tests/sync/G.8272/` (append `…/PRTC-A/` or `…/PRTC-B/` as appropriate).*

### Per-device tests (with [card-N])

| Test Path | Before | After |
|-----------|--------|-------|
| time-error-in-locked-mode/DPLL-to-PHC/PRTC-A | `.../DPLL-to-PHC/PRTC-A/?name=ens3f0&ptp_dev=/dev/ptp0&primary=true` | [Verify time error on path of DPLL to PHC in locked condition PRTC-A (Higher accuracy (e.g. for GNSS-based primary references)) [card-1]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-A/) |
| time-error-in-locked-mode/DPLL-to-PHC/PRTC-B | `.../DPLL-to-PHC/PRTC-B/?name=ens3f0&ptp_dev=/dev/ptp0&primary=true` | [Verify time error on path of DPLL to PHC in locked condition PRTC-B (Lower accuracy (e.g. for holdover or less precise references)) [card-1]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/DPLL-to-PHC/PRTC-B/) |
| time-error-in-locked-mode/SMA1-to-DPLL/PRTC-A | `.../SMA1-to-DPLL/PRTC-A/?name=ens3f1&...` | [Verify time error on path of SMA1 to DPLL in locked condition PRTC-A (Higher accuracy (e.g. for GNSS-based primary references)) [card-2]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/SMA1-to-DPLL/PRTC-A/) |
| time-error-in-locked-mode/SMA1-to-DPLL/PRTC-B | `.../SMA1-to-DPLL/PRTC-B/?name=ens3f1&...` | [Verify time error on path of SMA1 to DPLL in locked condition PRTC-B (Lower accuracy (e.g. for holdover or less precise references)) [card-2]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8272/time-error-in-locked-mode/SMA1-to-DPLL/PRTC-B/) |

*Same pattern for wander-TDEV and wander-MTIE variants of DPLL-to-PHC and SMA1-to-DPLL. TDEV tests include "TDEV (Time Deviation in locked mode)". MTIE tests include full expansion and "with a 0.1 Hz low-pass filter". PRTC-A and PRTC-B include accuracy descriptions. Card number depends on interface (ens3f0→card-1, ens3f1→card-2, etc.).*

---

## G.8273.2 (T-BC/T-TSC Mode) Tests

### Fixed tests (no device params)

| Test Path | Before | After |
|-----------|--------|-------|
| time-error-in-locked-mode/PHC-to-SYS/RAN | `https://github.com/.../sync/G.8273.2/time-error-in-locked-mode/PHC-to-SYS/RAN/` | [Verify time error on path of PHC to system clock in locked condition RAN](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/time-error-in-locked-mode/PHC-to-SYS/RAN/) |
| time-error-in-locked-mode/1PPS-to-DPLL/Class-C | `.../sync/G.8273.2/time-error-in-locked-mode/1PPS-to-DPLL/Class-C/` | [Verify time error on path of 1PPS input to 1PPS output of DPLL in locked condition Class-C](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/time-error-in-locked-mode/1PPS-to-DPLL/Class-C/) |
| time-error-in-locked-mode/PTP4L-to-PHC/Class-C | `.../sync/G.8273.2/time-error-in-locked-mode/PTP4L-to-PHC/Class-C/` | [Verify time error on path of PTP4L to PHC in locked condition Class-C](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/time-error-in-locked-mode/PTP4L-to-PHC/Class-C/) |
| phc/state-transitions | `.../sync/G.8273.2/phc/state-transitions/` | [Verify PHC state transitions](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/phc/state-transitions/) |

### Per-device tests (with [card-N])

| Test Path | Before | After |
|-----------|--------|-------|
| time-error-in-locked-mode/DPLL-to-PHC/Class-C | `.../DPLL-to-PHC/Class-C/?name=ens3f0&...` | [Verify time error on path of DPLL to PHC in locked condition Class-C [card-1]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/time-error-in-locked-mode/DPLL-to-PHC/Class-C/) |
| time-error-in-locked-mode/SMA1-to-DPLL/Class-C | `.../SMA1-to-DPLL/Class-C/?name=ens3f1&...` | [Verify time error on path of SMA1 to DPLL in locked condition Class-C [card-2]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/time-error-in-locked-mode/SMA1-to-DPLL/Class-C/) |
| TDEV-in-locked-mode/1PPS-to-DPLL/Class-C | `.../TDEV-in-locked-mode/1PPS-to-DPLL/Class-C/` | [Verify TDEV (Time Deviation in locked mode) on path of 1PPS input to 1PPS output of DPLL in locked condition Class-C](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/TDEV-in-locked-mode/1PPS-to-DPLL/Class-C/) |
| TDEV-in-locked-mode/DPLL-to-PHC/Class-C | `.../TDEV-in-locked-mode/DPLL-to-PHC/Class-C/?name=...` | [Verify TDEV (Time Deviation in locked mode) on path of DPLL to PHC in locked condition Class-C [card-N]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/TDEV-in-locked-mode/DPLL-to-PHC/Class-C/) |
| TDEV-in-locked-mode/SMA1-to-DPLL/Class-C | `.../TDEV-in-locked-mode/SMA1-to-DPLL/Class-C/?name=...` | [Verify TDEV (Time Deviation in locked mode) on path of SMA1 to DPLL in locked condition Class-C [card-N]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/TDEV-in-locked-mode/SMA1-to-DPLL/Class-C/) |
| TDEV-in-locked-mode/PTP4L-to-PHC/Class-C | `.../TDEV-in-locked-mode/PTP4L-to-PHC/Class-C/?name=...` | [Verify TDEV (Time Deviation in locked mode) on path of PTP4L to PHC in locked condition Class-C [card-N]](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/TDEV-in-locked-mode/PTP4L-to-PHC/Class-C/) |
| MTIE-for-LPF-filtered-series/1PPS-to-DPLL/Class-C | `.../MTIE-for-LPF-filtered-series/1PPS-to-DPLL/Class-C/` | [Verify MTIE (Maximum Time Interval Error) on path of 1PPS input to 1PPS output of DPLL in locked condition Class-C with a 0.1 Hz low-pass filter](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/MTIE-for-LPF-filtered-series/1PPS-to-DPLL/Class-C/) |
| MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C | `.../MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C/?name=...` | [Verify MTIE (Maximum Time Interval Error) on path of DPLL to PHC in locked condition Class-C [card-N] with a 0.1 Hz low-pass filter](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/MTIE-for-LPF-filtered-series/DPLL-to-PHC/Class-C/) |
| MTIE-for-LPF-filtered-series/SMA1-to-DPLL/Class-C | `.../MTIE-for-LPF-filtered-series/SMA1-to-DPLL/Class-C/?name=...` | [Verify MTIE (Maximum Time Interval Error) on path of SMA1 to DPLL in locked condition Class-C [card-N] with a 0.1 Hz low-pass filter](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/MTIE-for-LPF-filtered-series/SMA1-to-DPLL/Class-C/) |
| MTIE-for-LPF-filtered-series/PTP4L-to-PHC/Class-C | `.../MTIE-for-LPF-filtered-series/PTP4L-to-PHC/Class-C/?name=...` | [Verify MTIE (Maximum Time Interval Error) on path of PTP4L to PHC in locked condition Class-C [card-N] with a 0.1 Hz low-pass filter](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/G.8273.2/MTIE-for-LPF-filtered-series/PTP4L-to-PHC/Class-C/) |

---

## PTP Workload (if enabled)

| Test Path | Before | After |
|-----------|--------|-------|
| ptp-workload | `.../sync/ptp-workload/` | [Verify clock accuracy under PTP workload](https://github.com/redhat-partner-solutions/vse-sync-test/tree/main/tests/sync/ptp-workload/) |

---

## Summary of changes

1. **Full GitHub URL** → **Human-readable description** (in the PDF; in this doc the description links back to the tree URL)
2. **Query params** (`?name=ens3f0&ptp_dev=...`) → **Card label** (`[card-1]`, `[card-2]`, etc.)
3. **sync/G.8272/** and **sync/G.8273.2/** prefixes removed from titles
4. **Abbreviations** (1PPS, DPLL, PHC, etc.) kept as-is in descriptions for clarity
5. **PRTC-A** and **PRTC-B** include accuracy in parentheses after the label: PRTC-A = "PRTC-A (Higher accuracy (e.g. for GNSS-based primary references))"; PRTC-B = "PRTC-B (Lower accuracy (e.g. for holdover or less precise references))"
