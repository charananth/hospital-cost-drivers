"""Cohort summary tables."""
import numpy as np
import pandas as pd

import config
from src.features import safe_div


def yearly_summary(df):
    agg = df.groupby("YEAR").agg(
        hospitals=("FAC_NO", "nunique"),
        multi_report=("N_REPORTS", lambda s: (s > 1).sum()),
        over_366_days=("DAY_PER", lambda s: (s > 366).sum()),
        in_process=("DATA_IND", lambda s: (s == "IN PROCESS").sum()),
        missing_adj_days=("ADJPATDAYS", lambda s: s.isna().sum()),
        total_exp=("TOT_OP_EXP", "sum"),
        labor=("LABOR", "sum"),
        overhead_exp=("OVERHEAD_EXP", "sum"),
        discharges=("DIS_TOT", "sum"),
        fte=("FTE", "sum"),
        fte_patient=("FTE_PATIENT", "sum"),
        fte_overhead=("FTE_OVERHEAD", "sum"),
    )
    with_days = df[df["ADJPATDAYS"] > 0].groupby("YEAR")
    agg["adj_days"] = with_days["ADJPATDAYS"].sum()
    agg["cost_per_adj_day"] = safe_div(with_days["TOT_OP_EXP"].sum(), agg["adj_days"])
    agg["cost_per_fte"] = safe_div(agg["labor"], agg["fte"])
    agg["overhead_exp_per_fte"] = safe_div(agg["overhead_exp"], agg["fte"])
    agg["overhead_fte_share"] = safe_div(agg["fte_overhead"], agg["fte"])
    agg["labor_share_of_exp"] = safe_div(agg["labor"], agg["total_exp"])
    return agg


def add_real(summary, cpi):
    if cpi is None:
        return summary
    deflator = cpi.reindex(summary.index) / cpi[config.CPI_BASE_YEAR]
    out = summary.copy()
    for col in ["total_exp", "labor", "cost_per_adj_day", "cost_per_fte", "overhead_exp_per_fte"]:
        out[f"{col}_real"] = out[col] / deflator
    return out


def indexed(summary):
    cols = ["total_exp", "labor", "discharges", "adj_days", "fte", "cost_per_fte",
            "overhead_exp_per_fte", "cost_per_adj_day"]
    return summary[cols] / summary[cols].iloc[0] * 100


def variance_explained(df):
    """R^2 of total expense on employee cost, by year and pooled."""
    data = df.dropna(subset=["TOT_OP_EXP", "LABOR"])
    r2 = lambda d: np.corrcoef(d["LABOR"], d["TOT_OP_EXP"])[0, 1] ** 2
    by_year = {year: r2(d) for year, d in data.groupby("YEAR")}
    return pd.Series({**by_year, "pooled": r2(data)}, name="r2")


def expense_mix(df):
    totals = df.groupby("YEAR")[config.NATURAL_EXP_COLS + ["TOT_OP_EXP"]].sum()
    return totals[config.NATURAL_EXP_COLS].div(totals["TOT_OP_EXP"], axis=0)
