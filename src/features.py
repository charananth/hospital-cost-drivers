"""Hospital-level measures. Divide-by-zero gives NaN, never 0."""
import numpy as np

import config


def safe_div(a, b):
    return a.div(b.where(b != 0, np.nan))


def add_features(df):
    out = df.copy()
    out["LABOR"] = out["EXP_SAL"] + out["EXP_BEN"]
    # FTE-years from paid hours, so partial-year reports stay on one footing.
    out["FTE"] = out["PAID_HRS"] / config.HOURS_PER_FTE

    prd = lambda funcs: out[[f"PRD_HR_{f}" for f in funcs]].sum(axis=1, min_count=1)
    paid = lambda funcs: out[[f"PD_HR_{f}" for f in funcs]].sum(axis=1, min_count=1)

    prd_patient = prd(config.PATIENT_FUNCS)
    prd_overhead = prd(config.OVERHEAD_FUNCS)
    patient_share = safe_div(prd_patient, prd_patient + prd_overhead)
    out["PATIENT_SHARE"] = patient_share
    out["LABOR_PATIENT"] = out["LABOR"] * patient_share
    out["LABOR_OVERHEAD"] = out["LABOR"] * (1 - patient_share)
    out["FTE_PATIENT"] = paid(config.PATIENT_FUNCS) / config.HOURS_PER_FTE
    out["FTE_OVERHEAD"] = paid(config.OVERHEAD_FUNCS) / config.HOURS_PER_FTE

    out["OVERHEAD_EXP"] = out[config.OVERHEAD_EXP_COLS].sum(axis=1, min_count=1)
    out["COST_PER_ADJ_DAY"] = safe_div(out["TOT_OP_EXP"], out["ADJPATDAYS"])
    out["COST_PER_FTE"] = safe_div(out["LABOR"], out["FTE"])
    return out
