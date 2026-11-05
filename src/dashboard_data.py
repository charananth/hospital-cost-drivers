"""Write the dashboard's JSON files from outputs/: python -m src.dashboard_data"""
import json

import pandas as pd

import config

COHORTS = ["comparable", "balanced", "balanced_annualized"]
SUMMARY_COLS = [
    "hospitals", "in_process", "multi_report", "total_exp", "labor", "discharges",
    "adj_days", "fte", "cost_per_fte", "overhead_exp_per_fte", "cost_per_adj_day",
]
CATEGORIES = {
    "Salaries and benefits": ["EXP_SAL", "EXP_BEN"],
    "Physicians and professional fees": ["EXP_PHYS", "EXP_OTHPRO"],
    "Supplies": ["EXP_SUPP"],
    "Purchased services": ["EXP_PURCH"],
    "Depreciation, leases and interest": ["EXP_DEPRE", "EXP_LEASES", "EXP_INTRST"],
    "Insurance": ["EXP_INSUR"],
    "Other": ["EXP_OTH"],
}


def write(name, frame):
    path = config.OUTPUT_DIR / "dashboard" / name
    path.parent.mkdir(exist_ok=True)
    rows = json.loads(frame.to_json(orient="records", double_precision=4))
    path.write_text(json.dumps(rows))


def metrics():
    frames = []
    for cohort in COHORTS:
        folder = config.OUTPUT_DIR / cohort
        summary = pd.read_csv(folder / "summary.csv", index_col="YEAR")[SUMMARY_COLS]
        hospital = pd.read_csv(folder / "hospital_year.csv")
        overhead = hospital.groupby("YEAR")[config.OVERHEAD_EXP_COLS].sum()
        frames.append(summary.join(overhead).reset_index().assign(cohort=cohort))
    return pd.concat(frames).rename(columns=str.lower).rename(columns={"exp_fisc": "exp_fis"})


def decomposition():
    frames = [
        pd.read_csv(config.OUTPUT_DIR / c / "decomposition.csv").assign(cohort=c)
        for c in COHORTS
    ]
    out = pd.concat(frames)
    out["period"] = out["start"].astype(str) + "–" + out["end"].astype(str)
    return out[["cohort", "period", "start", "end", "group", "factor", "effect"]]


def expenses():
    frames = []
    for cohort in COHORTS:
        hospital = pd.read_csv(config.OUTPUT_DIR / cohort / "hospital_year.csv")
        for category, cols in CATEGORIES.items():
            totals = hospital.groupby("YEAR")[cols].sum().sum(axis=1)
            frames.append(totals.rename("dollars").reset_index().assign(
                cohort=cohort, category=category))
    return pd.concat(frames).rename(columns={"YEAR": "year"})


def hospitals():
    data = pd.read_csv(config.OUTPUT_DIR / "balanced" / "hospital_year.csv")
    wide = data.pivot(index="FAC_NO", columns="YEAR",
                      values=["COST_PER_ADJ_DAY", "COST_PER_FTE"])
    first, last = config.YEARS[0], config.YEARS[-1]
    names = data.sort_values("YEAR").groupby("FAC_NO")["FAC_NAME"].last()
    out = pd.DataFrame({
        "fac_no": wide.index.astype(str),
        "hospital": names.reindex(wide.index).to_numpy(),
        "day_start": wide["COST_PER_ADJ_DAY"][first].round(0).to_numpy(),
        "day_end": wide["COST_PER_ADJ_DAY"][last].round(0).to_numpy(),
        "fte_start": wide["COST_PER_FTE"][first].round(0).to_numpy(),
        "fte_end": wide["COST_PER_FTE"][last].round(0).to_numpy(),
    })
    out["day_multiple"] = (out["day_end"] / out["day_start"]).round(2)
    return out


if __name__ == "__main__":
    write("metrics.json", metrics())
    write("decomposition.json", decomposition())
    write("expenses.json", expenses())
    write("hospitals.json", hospitals())
