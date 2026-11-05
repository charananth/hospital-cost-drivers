"""All paths, column names and toggles for the hospital cost pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "Data" / "data_files_xlsx"
PIVOT_DIR = ROOT / "Data" / "pivot_tables"
CPI_PATH = ROOT / "Data" / "cpi_medical.csv"  # columns: YEAR, CPI
OUTPUT_DIR = ROOT / "outputs"

YEARS = [2004, 2009, 2014, 2019, 2024]
RAW_FILES = {
    2004: "cy-selected-file-hafd2004revised906.xls",
    2009: "cy-selected-file-hafd09-revised911.xlsx",
    2014: "hafd14-42017-extract.xlsx",
    2019: "hadr-19.xlsx",
    2024: "hadr-2024.xlsx",
}
PIVOT_FILES = {
    2004: "hafd2004pivot.xls",
    2009: "hafd2009pivot.xls",
    2014: "hafd2014pivot.xls",
    2019: "hafd2019pivot.xls",
    2024: "hafd2024pivot.xlsm",
}
PIVOT_SHEET = "Data"

# "comparable": TYPE_HOSP == Comparable, whatever reported each year.
# "balanced": comparable hospitals that report in every snapshot year.
# "all": every report, including Kaiser, PHF, State and LTC.
COHORT = "comparable"
COMPARABLE_LABEL = "COMPARABLE"

# Sum flows across partial-year reports as filed. True rescales each
# hospital-year to 365 days, for reports that overlap or run past a year.
ANNUALIZE = False

HOURS_PER_FTE = 2080
CPI_BASE_YEAR = 2024

# Names after load.normalize_columns; variants map to the canonical name.
COLUMN_ALIASES = {
    "ACCTS_0REC": "ACCTS_REC",
    "NAT_0BIRTHS": "NAT_BIRTHS",
    "CURR_LIAB": "CUR_LIAB",
    "DAY_PIPS": "DAYS_PIPS",
    "PD_HR_NO": "PD_HR_NON",
    "INTER-REC": "INTER_REC",
}

ID_COLS = ["FAC_NO", "FAC_NAME", "TYPE_HOSP", "DATA_IND"]
DATE_COLS = ["BEG_DATE", "END_DATE"]

PATIENT_FUNCS = ["DLY", "AMB", "ANC"]
OVERHEAD_FUNCS = ["ED", "GEN", "FIS", "ADM", "NON"]
PRD_HR_COLS = [f"PRD_HR_{f}" for f in PATIENT_FUNCS + OVERHEAD_FUNCS]
PD_HR_COLS = [f"PD_HR_{f}" for f in PATIENT_FUNCS + OVERHEAD_FUNCS]

NATURAL_EXP_COLS = [
    "EXP_SAL", "EXP_BEN", "EXP_PHYS", "EXP_OTHPRO", "EXP_SUPP", "EXP_PURCH",
    "EXP_DEPRE", "EXP_LEASES", "EXP_INSUR", "EXP_INTRST", "EXP_OTH",
]
OVERHEAD_EXP_COLS = ["EXP_RES", "EXP_ED", "EXP_GEN", "EXP_FISC", "EXP_ADM", "EXP_UNASSG"]

FLOW_COLS = [
    "DAY_PER", "TOT_OP_EXP", "DIS_TOT", "DAY_TOT", "PAID_HRS", "PROD_HRS",
    *NATURAL_EXP_COLS, *OVERHEAD_EXP_COLS, *PRD_HR_COLS, *PD_HR_COLS,
]
