"""Labor-cost decomposition: LMDI, so effects add up exactly to the change.

Within each group (patient, overhead):
    labor = adjusted days * FTE per adjusted day * cost per FTE
With CPI available, cost per FTE splits into a real part and medical inflation.
"""
import numpy as np
import pandas as pd

GROUPS = {"patient": ("LABOR_PATIENT", "FTE_PATIENT"),
          "overhead": ("LABOR_OVERHEAD", "FTE_OVERHEAD")}


def log_mean(a, b):
    return (a - b) / (np.log(a) - np.log(b)) if a != b else a


def usable(df):
    cols = ["LABOR_PATIENT", "LABOR_OVERHEAD", "FTE_PATIENT", "FTE_OVERHEAD", "ADJPATDAYS"]
    return df[(df[cols] > 0).all(axis=1)]


def group_factors(totals, labor_col, fte_col, cpi):
    labor, fte, days = totals[labor_col], totals[fte_col], totals["ADJPATDAYS"]
    factors = {"volume": days, "staffing": fte / days}
    if cpi is None:
        factors["wage"] = labor / fte
    else:
        factors["real_wage"] = labor / fte / cpi
        factors["inflation"] = cpi
    return labor, factors


def decompose(df, start, end, cpi=None):
    """Long table of effects for start -> end, in dollars, by group."""
    data = usable(df)
    totals = data.groupby("YEAR")[
        ["LABOR_PATIENT", "LABOR_OVERHEAD", "FTE_PATIENT", "FTE_OVERHEAD", "ADJPATDAYS"]
    ].sum()
    rows = []
    for group, (labor_col, fte_col) in GROUPS.items():
        labor, factors = group_factors(totals, labor_col, fte_col, cpi)
        weight = log_mean(labor[end], labor[start])
        for name, series in factors.items():
            rows.append({
                "start": start, "end": end, "group": group, "factor": name,
                "effect": weight * np.log(series[end] / series[start]),
                "labor_start": labor[start], "labor_end": labor[end],
            })
    out = pd.DataFrame(rows)
    out["share_of_change"] = out["effect"] / out["effect"].sum()
    return out


def decompose_all(df, years, cpi=None):
    pairs = list(zip(years[:-1], years[1:])) + [(years[0], years[-1])]
    return pd.concat([decompose(df, a, b, cpi) for a, b in pairs], ignore_index=True)


def check_identity(table):
    """Largest gap between summed effects and the actual labor change."""
    gaps = []
    for _, part in table.groupby(["start", "end", "group"]):
        actual = part["labor_end"].iloc[0] - part["labor_start"].iloc[0]
        gaps.append(abs(part["effect"].sum() - actual))
    return max(gaps)
