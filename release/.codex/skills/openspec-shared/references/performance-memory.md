# Performance and memory

Load this contract only when a change can plausibly affect performance or memory, or when it makes a quantitative claim. Omit it when no plausible effect exists.

## Planning contract

Identify the applicable hot paths, expected and worst-relevant workload, allocation and resource risks, latency and throughput, concurrency, buffering or batching, connection and pool lifecycle, backpressure, caching, serialization or conversion cost, benchmark or profile strategy, and existing regression thresholds.

## Evidence contract

| Situation | Required response |
|---|---|
| Quantitative claim | Measure it; record environment, versions, configuration, dataset, workload, command, repetitions, and result. |
| Suspected regression | Reproduce and diagnose the regression before optimizing. |
| Before-and-after comparison | Use the same representative workload and comparable environment; rerun correctness evidence as well as the measurement. |
| Existing threshold | Preserve and evaluate it; explain any deliberate change in the owning planning artifact. |
| No representative environment | State the limitation and use bounded alternate evidence without claiming a measured improvement. |

Prefer representative workloads over toy microbenchmarks. Inspect allocation, retention, cleanup, contention, queue growth, backpressure, caching, pooling, serialization, and buffering where relevant. Do not trade away correctness, public contracts, or resource cleanup without explicit artifact support.
