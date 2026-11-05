"""Type-fix, collapse partial-year reports, join pivots, select the cohort."""
import pandas as pd

import config


def coerce(df):
    df = df.copy()
    df[config.FLOW_COLS] = df[config.FLOW_COLS].apply(pd.to_numeric, errors="coerce")
    df[config.DATE_COLS] = df[config.DATE_COLS].apply(pd.to_datetime, errors="coerce")
    df["FAC_NO"] = pd.to_numeric(df["FAC_NO"], errors="coerce").astype("Int64")
    df["TYPE_HOSP"] = df["TYPE_HOSP"].astype(str).str.strip().str.upper()
    df["DATA_IND"] = df["DATA_IND"].astype(str).str.strip().str.upper()
    df["YEAR"] = df["END_DATE"].dt.year
    return df.dropna(subset=["FAC_NO", "YEAR"])


def collapse_reports(df):
    """One row per hospital-year: sum flows, keep the latest report's labels."""
    df = df.sort_values(["FAC_NO", "YEAR", "END_DATE"])
    keys = ["FAC_NO", "YEAR"]
    grouped = df.groupby(keys, sort=False)
    flows = grouped[config.FLOW_COLS].sum(min_count=1)
    labels = grouped[["FAC_NAME", "TYPE_HOSP", "DATA_IND", "END_DATE"]].last()
    begin = grouped["BEG_DATE"].min()
    n_reports = grouped.size().rename("N_REPORTS")
    return pd.concat([labels, begin, flows, n_reports], axis=1).reset_index()


def join_pivots(df, pivots):
    adjusted = (
        pivots.groupby(["FAC_NO", "YEAR"], as_index=False)
        .agg(ADJPATDAYS=("ADJPATDAYS", "sum"), PIVOT_DAY_PER=("DAY_PER", "sum"))
    )
    adjusted["FAC_NO"] = adjusted["FAC_NO"].astype("Int64")
    out = df.merge(adjusted, on=["FAC_NO", "YEAR"], how="left")
    # Pivots keep one report per hospital-year; scale to the days the raw reports cover.
    out["ADJPATDAYS"] = pd.to_numeric(out["ADJPATDAYS"], errors="coerce")
    out["PIVOT_DAY_PER"] = pd.to_numeric(out["PIVOT_DAY_PER"], errors="coerce")
    out["ADJ_DAYS_PRORATED"] = out["PIVOT_DAY_PER"] != out["DAY_PER"]
    out["ADJPATDAYS"] = out["ADJPATDAYS"] * out["DAY_PER"] / out["PIVOT_DAY_PER"]
    return out


def annualize(df):
    scale = 365 / df["DAY_PER"]
    cols = [c for c in config.FLOW_COLS if c != "DAY_PER"] + ["ADJPATDAYS"]
    out = df.copy()
    out[cols] = out[cols].mul(scale, axis=0)
    return out


def select_cohort(df, cohort):
    if cohort == "all":
        return df
    comparable = df[df["TYPE_HOSP"] == config.COMPARABLE_LABEL]
    if cohort == "comparable":
        return comparable
    if cohort == "balanced":
        counts = comparable.groupby("FAC_NO")["YEAR"].nunique()
        keep = counts[counts == len(config.YEARS)].index
        return comparable[comparable["FAC_NO"].isin(keep)]
    raise ValueError(f"unknown cohort: {cohort}")
