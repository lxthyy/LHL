# Which code is current

**All numbers, tables and figures in the manuscript come from the pipeline below.**
Two variance estimators are reported deliberately; they are not competing versions.

## Primary analyses (current)

Directory: `代码\_v136\` and `代码\_v137\`

| Script | Produces |
|---|---|
| `_v136\a_validate_baseline.py` | `结果表\_v136\cindex_with_baseline.csv`, `risk_scores.npy`, `sample_key.csv` |
| `_v136\b2_cluster_bootstrap_grid.py` | `equivalence_cluster_boot1000.csv`, `margin_grid_cluster.csv`, `simultaneous_band_cluster.csv` |
| `_v136\c_resolution_empirical.py` | `resolution_floor_empirical.csv` |
| `_v136\d_exposure_heterogeneity.py` | `exposure_reproduce.csv`, `exposure_heterogeneity.csv` |
| `_v136\e_figures.py` | Figure 1 and Figure 4 |
| `_v137\jackknife_g4.py` | **`结果表\_v136\jackknife_equivalence.csv`** — the source of Table 2 Panel B and Figure 1 intervals |

## Two estimators, both reported

- **Primary**: delete-one-PSU jackknife over 240 primary sampling units. Six of ten pairs
  are equivalent at a margin of 0.01.
- **Sensitivity**: 1,000-resample cluster bootstrap of primary sampling units. Seven of ten.
  The difference is HD − AL (jackknife upper bound 0.0104; bootstrap upper bound 0.0099).

The jackknife is primary because a concordance difference is a rank-based statistic and
resampling whole PSUs with replacement understates its variance. This is stated in Methods.

## Superseded — archived only, not used in any reported number

- `代码\_审校\` (internal review scripts, one-off checks and logs)
- `代码\b_cluster_bootstrap.py` (early version with 300 resamples)
- `结果表\加强\check_B300.csv`, `check_reproduce.csv` (early diagnostics)

They are retained for transparency. No number in the manuscript, tables or figures derives
from them.

## Reproduce

```
python 代码\_v136\a_validate_baseline.py
python 代码\_v136\b2_cluster_bootstrap_grid.py
python 代码\_v136\c_resolution_empirical.py
python 代码\_v137\jackknife_g4.py
python 代码\_v136\e_figures.py
```

Inputs are the frozen analytic datasets in `数据\`; no external download is required except
for `d_exposure_heterogeneity.py`, which reads the NHANES physical-activity files from a local
cache (the derived `数据\paq_active.csv` is provided, so the manuscript numbers do not depend
on that step).

Number-to-table-to-script mapping: `数字溯源对照_v1.37.md`.
Environment and package versions: `环境清单_v1.36.txt`.

## A note on language

Some scripts retain comments in Chinese from the original working notes. Variable names,
function names and all console output are in English, and no analysis logic depends on the
comments.

## Licence

Data and documentation: CC BY 4.0. Code: MIT.
