# CLAUDE.md — Hospital Cost Drivers

Context for continuing this project in Claude Code.

## What this is
California HCAI hospital financial data, 5 snapshot years (2004/09/14/19/24),
for Prof. Melnick (USC Price School). Question: **what drives hospital operating
costs up?** This repo consolidates three messy exploratory notebooks into one
pipeline.

## The finding (through-line)
For the 310 comparable hospitals in all 5 years, costs ~3.5x'd 2004->2024.
Discharges were flat, but adjusted patient days rose ~35% and FTEs ~50%. Cost per
FTE (2.1x) is ~65% of employee-cost growth; employee cost is ~46% of total expense
growth. Employee cost vs expense R² is ~0.97 for comparable hospitals, but that
mostly reflects hospital size. The core analysis is the **labor-cost decomposition
(headcount vs wage), split patient vs overhead** — Melnick's actual ask.

## How it's built
`config.py` (all paths/columns/toggles) -> `src/`: load -> clean -> features ->
decompose -> analysis -> plots -> pipeline.
Run: `python -m src.pipeline --cohort comparable` -> outputs to `outputs/`.

## Key decisions
- **Raw** = HCAI "CY Hospital Annual Selected File" (`hadr-<yr>.xlsx`); **pivots**
  supply adjusted patient days. Loader reads `.xlsx` or `.csv` directly.
- **YEAR** = year of END_DATE. Partial-year duplicate reports collapsed (sum flows).
- **Cohort** = comparable hospitals (toggle in `config.COHORT`).
- Dollars **nominal + inflation-adjusted** (medical CPI). Salary split by
  productive-hour share. Divide-by-zero -> NaN (not 0). All vectorized.

## Data (data.chhs.ca.gov -> "Hospital Annual Financial Data - Selected Data & Pivot Tables")
`Data/data_files_xlsx/` = raw files (names vary by year, mapped in
`config.RAW_FILES`); `Data/pivot_tables/` = `hafd<yr>pivot.xls[m]`.
NOT the Utilization report, NOT the Complete Data Set. Use `.venv` (`requirements.txt`).

## Gotcha
HCAI column names drift by year (e.g. `NAT_ BIRTHS` vs `NAT_0BIRTHS`) — handled via
`config.COLUMN_ALIASES`. If the loader's "missing columns" warning fires on
2004/09/14, add the variant there.

## Status / to finish
Pipeline built and run on all 5 years + pivots (cohorts: `comparable`, `balanced`,
`all`; `--annualize` sensitivity). Reconciled against the 3 notebooks in
`analysis_NB/`. They differ mainly because they keep 357 hospitals, including Kaiser
(no employee cost until 2024). Overhead follows the notebooks: research, education,
general, fiscal, administrative, unassigned. `python -m src.dashboard_data` rebuilds
the dashboard files. `analysis_walkthrough.ipynb` explains every step (kernel:
`price_lab`). Left: build `Data/cpi_medical.csv` (YEAR, CPI), `git init` -> push.
