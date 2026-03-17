# PTP Workload System Test

Workload-based system tests that **consume PTP events**, **stress the system**, and **validate clock accuracy** under load. These differ from path-validation tests (e.g. `system-test-PHC-to-SYS`) which only verify the sync path without workload.

## Purpose

- **Consume PTP events**: Continuously read PHC timestamps (`phc_ctl cmp`) to simulate a RAN-style consumer
- **Stress the system**: Optional CPU load to stress the node while PTP is active
- **Validate clock**: Ensure time error stays within RAN limit (< 100 ns) during the workload

## Components

| File | Description |
|------|-------------|
| `ptp_workload.py` | Python workload: reads PHC, optional CPU stress, validates clock |
| `ptp_workload.sh` | Shell version (minimal dependencies) |
| `run_workload_test.sh` | Runs workload inside linuxptp-daemon pod via `oc exec` |
| `ptp_workload_job.yaml` | Kubernetes Job to run workload in-cluster |

## Usage

### From host (against running cluster)

```bash
# Run 300s workload (default)
KUBECONFIG=/path/to/kubeconfig ./run_workload_test.sh

# Run 600s workload
./run_workload_test.sh /path/to/kubeconfig 600

# Custom namespace
PTP_NAMESPACE=my-ptp-ns ./run_workload_test.sh
```

### Inside container (linuxptp-daemon)

```bash
# With Python available
python3 ptp_workload.py --duration 300 --phc-dev /dev/ptp0 --stress-cpu

# Without Python (shell)
./ptp_workload.sh 300 /dev/ptp0
```

### Kubernetes Job

```bash
oc apply -f ptp_workload_job.yaml
oc logs -f job/ptp-workload-system-test
```

## Output

JSON with `result` (pass/fail), `max_time_error_ns`, `samples`, `limit_ns` (100 ns RAN requirement).

When run from e2e with 0 samples, a diagnostic file is written to `data/artefacts/ptp_workload_phc_ctl_sample.txt` containing the raw `phc_ctl cmp` output for debugging.

## Requirements

- `phc_ctl` in PATH (from linuxptp)
- PHC device (e.g. `/dev/ptp0`)
- For `run_workload_test.sh`: `oc`, `KUBECONFIG`, linuxptp-daemon pod in cluster
