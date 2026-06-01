# Motivation single-thread 256-slot competitor benchmark

## Goal

Measure single-thread throughput with memory collection for ART, ALEX, LIPP, ALEX-256slot, and LIPP-256slot under the motivation configuration: uniform sampling, 100M bulkload, shuffled insert, no tail-latency sampling, repeated three times.

## Design

The run used the PR branch `add-256slot-competitors` at commit `056ef0f46167be85c62c804e811f0bb7d2de2c8a` when the tmux job was started. The benchmark executable was the existing Release build in this worktree.

Configuration:

- Dataset source: `/root/workspace/datasets`, symlinked into `datasets/`
- Datasets: `linear`, `covid`, `fb-1`, `osm`
- Indexes: `art`, `alex`, `lipp`, `alex-256slot`, `lipp-256slot`
- Repeats: 3
- Threads: 1 (`--thread_num=1`, `taskset -c 1`)
- NUMA binding: `numactl --cpunodebind=0 --membind=0`
- Sampling: uniform shuffled insert (`--test_suite=22`)
- Bulkload size: 100M (`--init_table_ratio=0.5` over 200M-key datasets)
- Memory collection: enabled (`--memory`)
- Tail latency sampling: disabled; no `--latency_sample` flag
- Random seed: benchmark default `1866`

## Validation Method

The benchmark campaign ran detached in tmux session `robin-256slot-motivation`. Each index/dataset/repeat invocation used:

```bash
numactl --cpunodebind=0 --membind=0 taskset -c 1 \
  ./build/microbench \
  --keys_file_type=binary \
  --read=0.0 --insert=0.0 --update=0.0 --scan=0.0 --delete=0.0 \
  --test_suite=22 \
  --operations_num=0 \
  --table_size=-1 \
  --init_table_ratio=0.5 \
  --del_table_ratio=0.0 \
  --thread_num=1 \
  --preload_suite=0 \
  --memory \
  --output_path=result/motivation/motivation_single_thread_uniform_100m_shuffled_raw.csv \
  --keys_file=datasets/<dataset> \
  --index=<index>
```

The raw CSV contains 120 rows: 4 datasets × 5 indexes × 3 repeats × 2 measured phases (`insert_ratio=1` and `read_ratio=1`). A post-run aggregation verified that every dataset/index pair has three insert rows and three read rows.

## Results

Raw artifacts:

- Raw benchmark CSV: `result/motivation/motivation_single_thread_uniform_100m_shuffled_raw.csv`
- Aggregated CSV: `result/motivation/motivation_single_thread_uniform_100m_shuffled_summary.csv`
- Markdown result table: `result/motivation/motivation_single_thread_uniform_100m_shuffled.md`
- Run log: `result/motivation/motivation_single_thread_uniform_100m_shuffled_run.log`
- Completion status: `result/motivation/motivation_single_thread_uniform_100m_shuffled_status.txt`

Summary table from `result/motivation/motivation_single_thread_uniform_100m_shuffled.md`:

| Dataset   | Index        |   Repeats |   Insert throughput avg (Mops/s) |   Read throughput avg (Mops/s) |   Memory (GiB) |
|:----------|:-------------|----------:|---------------------------------:|-------------------------------:|---------------:|
| linear    | art          |         3 |                            2.267 |                          2.671 |          4.482 |
| linear    | alex         |         3 |                            2.548 |                          7.285 |          3.814 |
| linear    | lipp         |         3 |                            8.991 |                         10.925 |          2.980 |
| linear    | alex-256slot |         3 |                            0.842 |                          1.144 |          4.659 |
| linear    | lipp-256slot |         3 |                            0.566 |                          1.596 |         19.147 |
| covid     | art          |         3 |                            1.516 |                          1.772 |          7.829 |
| covid     | alex         |         3 |                            1.754 |                          4.796 |          3.830 |
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
| osm       | lipp         |         3 |                            1.022 |                          2.010 |         23.649 |
| osm       | alex-256slot |         3 |                            0.659 |                          0.970 |          4.700 |
| osm       | lipp-256slot |         3 |                            0.560 |                          1.244 |         24.279 |

## Conclusions and remaining uncertainty

- The requested motivation table was produced for all requested indexes, datasets, and repeats.
- The 256-slot variants use more constrained node sizing and, in this configuration, generally trade lower throughput for different memory footprints versus the original implementations.
- These results were produced from a working tree with uncommitted benchmark artifacts before this report commit, so they should be treated as a PR-local motivation record rather than a decision-grade release benchmark.
- No tail-latency conclusions are supported by this run because latency sampling was intentionally disabled.
