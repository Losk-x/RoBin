# ALEX-256slot low-load-factor tuning probe

## Goal

Evaluate whether lowering ALEX-256slot data-node occupancy thresholds can move memory usage toward ART under the existing 256-slot cap while preserving the original `alex` and `alex-256slot` baselines.

## Design

Added an isolated competitor variant, `alex-256slot-lowlf`, copied from `alex-256slot` and registered as a separate benchmark index. The variant keeps the 256-slot data-node and fanout caps, but changes only the copied data-node density constants:

- `kMaxDensity_`: `0.8` -> `0.6`
- `kInitDensity_`: `0.7` -> `0.5`
- `kMinDensity_`: `0.6` -> `0.4`

An earlier exploratory build with `0.4 / 0.35 / 0.3` was rejected after full-size runs crashed during bulk load, so it was not kept as the implementation.

## Validation Method

Build:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --target microbench -j
```

Correctness sanity:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('datasets/linear-500.txt')
p.write_text('\n'.join(str(i) for i in range(1, 501)) + '\n')
PY
./build/microbench --keys_file=datasets/linear-500.txt --keys_file_type=text --read=0.0 --insert=0.0 --update=0.0 --scan=0.0 --delete=0.0 --test_suite=21 --operations_num=0 --table_size=500 --init_table_ratio=0.5 --del_table_ratio=0.0 --thread_num=1 --index=alex-256slot-lowlf --preload_suite=0 --memory
```

Observed sanity result for `alex-256slot-lowlf`: `success_insert: 250`, `success_read: 500`.

Benchmark command pattern:

```bash
numactl --cpunodebind=0 --membind=0 taskset -c 1 ./build/microbench \
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
  --output_path=result/motivation/alex_256slot_lowlf_single_thread_uniform_100m_shuffled_raw.csv \
  --keys_file=/root/workspace/datasets/<dataset> \
  --index=art,alex-256slot,alex-256slot-lowlf
```

Datasets were read from `/root/workspace/datasets/{linear,covid,fb-1,osm}`. Each file was present and 1,600,000,008 bytes. The benchmark used one repeat per dataset/index with 100M bulkload and 100M shuffled inserts, matching the motivation benchmark configuration.

## Results

Raw and summarized artifacts:

- `result/motivation/alex_256slot_lowlf_single_thread_uniform_100m_shuffled_raw.csv`
- `result/motivation/alex_256slot_lowlf_single_thread_uniform_100m_shuffled_summary.csv`
- `result/motivation/alex_256slot_lowlf_single_thread_uniform_100m_shuffled.md`

| Dataset | Index | Insert Mops/s | Read Mops/s | Memory GiB | Memory / ART | Target |
|---|---|---:|---:|---:|---:|---|
| linear | art | 2.257 | 2.578 | 4.482 | 1.000 | baseline |
| linear | alex-256slot | 0.861 | 1.162 | 4.659 | 1.039 | yes |
| linear | alex-256slot-lowlf | 0.781 | 1.146 | 6.867 | 1.532 | no |
| covid | art | 1.547 | 1.778 | 7.829 | 1.000 | baseline |
| covid | alex-256slot | 0.800 | 1.181 | 4.649 | 0.594 | no |
| covid | alex-256slot-lowlf | 0.698 | 0.985 | 6.984 | 0.892 | no |
| fb-1 | art | 1.202 | 1.002 | 9.794 | 1.000 | baseline |
| fb-1 | alex-256slot | 0.522 | 0.677 | 4.968 | 0.507 | no |
| fb-1 | alex-256slot-lowlf | 0.479 | 0.607 | 7.305 | 0.746 | no |
| osm | art | 1.327 | 1.691 | 9.518 | 1.000 | baseline |
| osm | alex-256slot | 0.654 | 0.965 | 4.700 | 0.494 | no |
| osm | alex-256slot-lowlf | 0.604 | 0.863 | 7.026 | 0.738 | no |

Target means memory greater than ART and no more than ART * 1.10 for the same dataset.

## Conclusions and Remaining Uncertainty

The isolated low-load-factor variant changes memory in the intended direction for `covid`, `fb-1`, and `osm`, but it does not meet the target. It overshoots badly on `linear` and remains below ART on the other three datasets.

This indicates that a single global density triple is too blunt for the stated cross-dataset target under the fixed 256-slot cap. The remaining gap is not just leaf slack: lowering density increases memory roughly uniformly, while ART memory varies strongly by key distribution. Further tuning should inspect ALEX model-node/data-node composition and consider a distribution-sensitive or structure-sensitive control if exact ART-relative memory matching is required. That would be a benchmark-methodology change and should remain isolated as a separate experimental variant.
