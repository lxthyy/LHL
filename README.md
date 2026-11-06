# LHL — Equivalence of biological age indices

Analysis code, derived datasets and result tables for a meta-research study of head-to-head
comparisons between five biological age indices in 34,393 US adults (NHANES 1999–2018),
with a structured audit of 22 published comparisons.

Manuscript under review. This repository is the reproducibility package referenced in the
Data sharing statement.

## What is here

```
code/      analysis scripts (Python 3.11)
results/   every intermediate result table (CSV / NumPy)
data/      derived analytic datasets (CSV)
docs/      reproduction notes, environment, number-to-source map
```

Sub-directories:

- `code/v136/`, `results/v136/` — the analysis that produces the numbers in the manuscript
- `code/v137/`, `results/v136/jackknife_equivalence.csv` — delete-one-PSU jackknife
- `code/amplification/`, `results/amplification/` — sensitivity analyses
- `results/ten-cycle/` — ten-cycle extension
- `code/internal-review/` — internal audit scripts, archived, not part of any reported number

## Current estimand

The primary variance estimator is a **delete-one-PSU jackknife** over 240 pseudo-strata
(2,000 resamples of the design). The paired PSU-cluster bootstrap (1,000 resamples) is
retained as a **sensitivity analysis**. The two differ on one pair, HD − AL:

| method | ΔC | 95% interval | equivalent at ±0.01 |
|---|---|---|---|
| jackknife (primary) | 0.0090 | 0.0076 – 0.0104 | no |
| cluster bootstrap | 0.0090 | 0.0081 – 0.0099 | yes |

Equivalence counts at ±0.005 / ±0.01 / ±0.015 are 2 / 6 / 10 under the jackknife.

## Reproduce

```
pip install -r docs/requirements-not-pinned.txt   # or see docs/环境清单_v1.36.txt
cd code/v136
python a_validate_baseline.py
python b2_cluster_bootstrap_grid.py
python c_resolution_empirical.py
```

Inputs are the CSVs in `data/`; nothing is downloaded at run time. NHANES source files and
the extraction logic are described in `docs/复现说明_v1.36.md`.

## Notes

- Some scripts retain comments in Chinese from the original working notes. Variable names,
  function names and console output are in English; no analysis logic depends on comments.
- Scripts are numbered in execution order. `code/v137/` must be run after `code/v136/`.

## Licence

Code: MIT (`LICENSE-MIT.txt`). Data and documentation: CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`).
