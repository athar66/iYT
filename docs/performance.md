# Measured performance

`reports/benchmark.json` records five host runs per variant of the same original synthetic native player workload. It uses a fake decoder, fake time and local files. Both variants preserve the original shown/dropped/decoded counters and end-of-stream behaviour.

The short wall-time samples are dominated by process startup and filesystem/cache noise; do not interpret small differences as an optimisation gain. No vehicle CPU, GPU, start latency, battery, cluster bandwidth or long-running leak figures were measured. Performance targets from the brief remain targets.

Actual structural limits: original three-frame presentation queue retained, new 16MiB NAL/access-unit guards, 32MiB MP4 box guard, 4096-record native index read batches and 2M record ceiling. Cluster routing throttles at 8/10/12fps and drops when the client already has a frame waiting. Transport compression/governor is upstream cluster-render's responsibility; adapter submittedBytes counts raw payload submitted, not measured transport bytes.
