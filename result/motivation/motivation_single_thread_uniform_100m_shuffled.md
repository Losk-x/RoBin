# Motivation single-thread throughput, uniform 100M shuffled insert

Configuration:

- Dataset source: `/root/workspace/datasets` symlinked into `datasets/`
- Datasets: `linear`, `covid`, `fb-1`, `osm`
- Indexes: `art`, `alex`, `lipp`, `alex-256slot`, `lipp-256slot`
- Repeats: 3
- Threads: 1 (`taskset -c 1`)
- NUMA binding: `numactl --cpunodebind=0 --membind=0`
- Sampling: uniform (`test_suite=22`)
- Bulkload size: 100M (`init_table_ratio=0.5` over 200M keys)
- Insert pattern: shuffled
- Memory collection: enabled (`--memory`)
- Tail latency sampling: disabled
- Raw output: `result/motivation/motivation_single_thread_uniform_100m_shuffled_raw.csv`
- Run log: `result/motivation/motivation_single_thread_uniform_100m_shuffled_run.log`

| Dataset   | Index        |   Repeats |   Insert throughput avg (Mops/s) |   Read throughput avg (Mops/s) |   Memory (GiB) |
|:----------|:-------------|----------:|---------------------------------:|-------------------------------:|---------------:|
| linear    | art          |         3 |                            2.267 |                          2.671 |          4.482 |
| linear    | alex         |         3 |                            2.548 |                          7.285 |          3.814 |
| linear    | lipp         |         3 |                            8.991 |                         10.925 |          2.98  |
| linear    | alex-256slot |         3 |                            0.842 |                          1.144 |          4.659 |
| linear    | lipp-256slot |         3 |                            0.566 |                          1.596 |         19.147 |
| covid     | art          |         3 |                            1.516 |                          1.772 |          7.829 |
| covid     | alex         |         3 |                            1.754 |                          4.796 |          3.83  |
| covid     | lipp         |         3 |                            2.293 |                          2.916 |         16.772 |
| covid     | alex-256slot |         3 |                            0.796 |                          1.164 |          4.649 |
| covid     | lipp-256slot |         3 |                            0.454 |                          1.118 |         28.952 |
| fb-1      | art          |         3 |                            1.157 |                          0.979 |          9.794 |
| fb-1      | alex         |         3 |                            0.719 |                          1.183 |          4.426 |
| fb-1      | lipp         |         3 |                            1.061 |                          1.915 |         19.521 |
| fb-1      | alex-256slot |         3 |                            0.518 |                          0.675 |          4.968 |
| fb-1      | lipp-256slot |         3 |                            0.463 |                          1.149 |         23.384 |
| osm       | art          |         3 |                            1.386 |                          1.561 |          9.518 |
| osm       | alex         |         3 |                            0.902 |                          1.836 |          4.267 |
| osm       | lipp         |         3 |                            1.022 |                          2.01  |         23.649 |
| osm       | alex-256slot |         3 |                            0.659 |                          0.97  |          4.7   |
| osm       | lipp-256slot |         3 |                            0.56  |                          1.244 |         24.279 |
