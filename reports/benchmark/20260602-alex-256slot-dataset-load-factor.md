# ALEX-256slot dataset-specific load-factor tuning

## Goal

Find dataset-specific ALEX-256slot load-factor variants for `covid`, `fb-1`, and `osm` whose memory usage is close to ART, then compare throughput.

The acceptance target is memory within 10% of ART on the same dataset. This follow-up intentionally excludes `linear` and does not require one shared configuration across all datasets.

## Design

Added three isolated competitors copied from `alex-256slot`, preserving `alex` and `alex-256slot` as baselines:

| Variant | kMaxDensity_ | kInitDensity_ | kMinDensity_ | Intended dataset |
|---|---:|---:|---:|---|
| `alex-256slot-lf024` | 0.6 | 0.5 | 0.24 | `covid` |
| `alex-256slot-lf020` | 0.6 | 0.5 | 0.20 | `fb-1` |
| `alex-256slot-lf019` | 0.6 | 0.5 | 0.19 | `osm` |

The index name encodes the tuned lower density. All variants retain the 256-slot node/fanout cap from `alex-256slot`.

Quick iteration probes rejected:

- `kInitDensity_=0.45`, `kMinDensity_=0.35`: full-size bulk load crashed.
- `kMinDensity_=0.30` and `0.50`: stable, but memory remained too low.
- `kMinDensity_=0.24`: met the target for `covid`, but remained too low for `fb-1` and `osm`.
- `kMinDensity_=0.20`: met the target for `fb-1` and `osm`; `0.19` was slightly closer for `osm` and remained within target.

## Validation Method

Benchmarked commit: `36f63c9` (`perf(competitor): add dataset-specific ALEX load-factor variants`).
Build:

```bash
cmake --build build --target microbench -j
```

Correctness sanity, run for each new variant on a temporary 500-key text dataset:

```bash
./build/microbench --keys_file=datasets/linear-500.txt --keys_file_type=text --read=0.0 --insert=0.0 --update=0.0 --scan=0.0 --delete=0.0 --test_suite=21 --operations_num=0 --table_size=500 --init_table_ratio=0.5 --del_table_ratio=0.0 --thread_num=1 --index=<variant> --preload_suite=0 --memory
```

Observed for each of `alex-256slot-lf019`, `alex-256slot-lf020`, and `alex-256slot-lf024`: `success_insert: 250`, `success_read: 500`.

Acceptance benchmark pattern:

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
  --output_path=result/motivation/alex_256slot_dataset_load_factor_raw.csv \
  --keys_file=/root/workspace/datasets/<dataset> \
  --index=art,alex-256slot,<dataset-specific-variant>
```

Datasets: `/root/workspace/datasets/{covid,fb-1,osm}`. Each benchmark row uses the existing `test_suite=22` 100M bulkload / 100M shuffled-insert setup. Acceptance ran three repeats for every dataset/index/phase combination.

## Results

Artifacts:

- `result/motivation/alex_256slot_dataset_load_factor_raw.csv`
- `result/motivation/alex_256slot_dataset_load_factor_summary.csv`
- `result/motivation/alex_256slot_dataset_load_factor.md`

| Dataset | Index | Repeats | Insert Mops/s avg | Read Mops/s avg | Memory GiB | Memory / ART | Target |
|---|---|---:|---:|---:|---:|---:|---|
| covid | art | 3 | 1.729 | 2.043 | 7.829 | 1.000 | baseline |
| covid | alex-256slot | 3 | 0.909 | 1.410 | 4.649 | 0.594 | no |
| covid | alex-256slot-lf024 | 3 | 0.834 | 1.222 | 7.975 | 1.019 | yes |
| fb-1 | art | 3 | 1.404 | 1.243 | 9.794 | 1.000 | baseline |
| fb-1 | alex-256slot | 3 | 0.599 | 0.845 | 4.968 | 0.507 | no |
| fb-1 | alex-256slot-lf020 | 3 | 0.565 | 0.800 | 9.869 | 1.008 | yes |
| osm | art | 3 | 1.575 | 1.826 | 9.518 | 1.000 | baseline |
| osm | alex-256slot | 3 | 0.636 | 0.947 | 4.700 | 0.494 | no |
| osm | alex-256slot-lf019 | 3 | 0.600 | 0.854 | 10.034 | 1.054 | yes |

## Conclusions and Remaining Uncertainty

Dataset-specific lower-density variants meet the memory target for all three requested datasets:

- `covid`: `alex-256slot-lf024`, 1.9% above ART.
- `fb-1`: `alex-256slot-lf020`, 0.8% above ART.
- `osm`: `alex-256slot-lf019`, 5.4% above ART.

Performance cost versus baseline `alex-256slot` is modest relative to the memory increase:

- `covid`: insert -8.2%, read -13.4%.
- `fb-1`: insert -5.6%, read -5.3%.
- `osm`: insert -5.8%, read -9.8%.

ART remains faster than both ALEX-256slot and the tuned variants in these runs. The tuned variants are useful for controlled memory-matched comparisons, not as throughput improvements.
