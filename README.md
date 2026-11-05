# hospital-cost-drivers
Reproducible Python pipeline analyzing 20 years of California hospital financial data (HCAI) to identify drivers of operating-cost growth.

## The question
What drives hospital operating costs up? The analysis uses HCAI annual financial
reports for five snapshot years (2004, 2009, 2014, 2019, 2024). It splits growth in
employee cost into three parts:

- **Volume:** more adjusted patient days
- **Staffing:** more FTEs per adjusted patient day
- **Cost per FTE:** higher salaries and benefits per FTE

It also splits that growth between patient care and overhead.

## Main results
These figures cover the 310 comparable hospitals that report in all five years.
They're in nominal dollars, not adjusted for inflation.

| Measure | 2004 | 2024 | Change |
|---|---|---|---|
| Total operating expense | $41.4B | $143.3B | 3.46x |
| Employee cost (salaries + benefits) | $21.5B | $68.9B | 3.20x |
| Cost per FTE | $70,955 | $151,838 | 2.14x |
| FTEs | 303,343 | 453,785 | 1.50x |
| Adjusted patient days | 21.0M | 28.3M | 1.35x |
| Discharges | 2.67M | 2.70M | 1.01x |

Of the $47.4B rise in employee cost, 65% came from cost per FTE, 26% from volume
and 9% from staffing. Employee cost accounts for 46.5% of the growth in total
expense, so most of the increase comes from other costs.

## How to reproduce it

### 1. Set up Python
You need Python 3.11 or later. The analysis was run on 3.12.

```bash
git clone https://github.com/charananth/hospital-cost-drivers.git
cd hospital-cost-drivers
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

### 2. Run the pipeline
```bash
python -m src.pipeline --cohort balanced
```

Results go to `outputs/<cohort>/`. Options:

- `--cohort balanced`: comparable hospitals that report in all five years. The headline results use this group.
- `--cohort comparable`: every comparable hospital that reports in a given year. This is the default.
- `--cohort all`: every report, including Kaiser, psychiatric, state and long-term-care hospitals.
- `--annualize`: rescales each hospital-year to 365 days. Use it to check how much partial-year reports matter.

The run stops with an error if the parts of the breakdown don't add up to the
total change. To rebuild the JSON files used by the dashboard, run
`python -m src.dashboard_data` after the pipeline.

### 3. Read the walkthrough
`analysis_walkthrough.ipynb` explains each step with the code and its output: load,
clean, measures, the breakdown, costs beyond labor, and how sensitive the results
are to each choice.

```bash
python -m notebook analysis_walkthrough.ipynb
```

## Repository layout
| Path | Contents |
|---|---|
| `config.py` | All file paths, column names and settings |
| `src/load.py` | Reads the raw files and pivot tables, and standardizes column names |
| `src/clean.py` | Sets the year, combines partial-year reports, and selects the hospital group |
| `src/features.py` | FTEs, employee cost, and the patient vs. overhead split |
| `src/decompose.py` | Breaks employee-cost growth into volume, staffing and cost per FTE |
| `src/analysis.py`, `src/plots.py` | Yearly summaries, expense mix and charts |
| `src/pipeline.py` | Runs every step and writes `outputs/` |
| `Data/data_files_xlsx/` | Raw HCAI annual financial files, one per year |
| `Data/pivot_tables/` | HCAI pivot tables, which supply adjusted patient days |
| `Data/data_files_csv/` | CSV copies of the expense data, used in the walkthrough's comparison with the old notebooks |
| `analysis_NB/` | The earlier exploratory notebooks. The walkthrough explains why their numbers differ. |
| `outputs/` | Results for each hospital group: summary tables, the breakdown and charts |

## Data
The source is the California Department of Health Care Access and Information (HCAI),
"Hospital Annual Financial Data - Selected Data & Pivot Tables," on
[data.chhs.ca.gov](https://data.chhs.ca.gov). The files are copied here unchanged.

## Key choices
- **Year:** each report counts toward the year its reporting period ends.
- **Partial-year reports:** when a hospital filed more than one report for a year, the reports are added together.
- **FTEs:** paid hours divided by 2,080.
- **Employee cost:** salaries plus benefits. Physician and contract labor aren't included.
- **Patient vs. overhead pay:** salaries are split by each area's share of productive hours.
- **Overhead expense:** research, education, general services, fiscal services, administration and unassigned costs.
- **Missing values:** when a calculation would divide by zero, the result is left blank.

## Limits
- **Inflation:** all dollars are nominal. The code can adjust for inflation once a CPI file is added at `Data/cpi_medical.csv`, with columns `YEAR` and `CPI`.
- **2024 data:** most 2024 reports were still unaudited when downloaded, so those figures may change.
- **Patient vs. overhead split:** it follows hours worked, so it doesn't show which group's pay rose faster.
