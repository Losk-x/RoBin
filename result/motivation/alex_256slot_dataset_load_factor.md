# ALEX-256slot dataset-specific load-factor tuning

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

Target is memory within ±10% of ART for the same dataset. Tuned variants use kMaxDensity=0.6, kInitDensity=0.5, and dataset-specific kMinDensity encoded in the index name.
