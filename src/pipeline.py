"""Run everything: python -m src.pipeline --cohort comparable"""
import argparse

import pandas as pd

import config
from src import analysis, clean, decompose, features, load, plots


def load_cpi():
    if not config.CPI_PATH.exists():
        print(f"WARNING: {config.CPI_PATH} not found; reporting nominal dollars only")
        return None
    return pd.read_csv(config.CPI_PATH).set_index("YEAR")["CPI"]


def build(cohort, annualize):
    raw = clean.coerce(load.load_raw())
    wrong_year = raw[raw["YEAR"] != raw["FILE_YEAR"]]
    if len(wrong_year):
        print(f"WARNING: {len(wrong_year)} reports end outside their file's year")
    data = clean.collapse_reports(raw)
    data = clean.join_pivots(data, load.load_pivots())
    if annualize:
        data = clean.annualize(data)
    return features.add_features(clean.select_cohort(data, cohort))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", default=config.COHORT,
                        choices=["comparable", "balanced", "all"])
    parser.add_argument("--annualize", action="store_true", default=config.ANNUALIZE)
    args = parser.parse_args()

    out = config.OUTPUT_DIR / (args.cohort + ("_annualized" if args.annualize else ""))
    out.mkdir(parents=True, exist_ok=True)

    cpi = load_cpi()
    data = build(args.cohort, args.annualize)
    summary = analysis.add_real(analysis.yearly_summary(data), cpi)
    index = analysis.indexed(summary)
    effects = decompose.decompose_all(data, config.YEARS, cpi)
    gap = decompose.check_identity(effects)
    if gap > 1:
        raise RuntimeError(f"decomposition does not add up: off by ${gap:,.0f}")

    data.to_csv(out / "hospital_year.csv", index=False)
    summary.to_csv(out / "summary.csv")
    index.to_csv(out / "index.csv")
    effects.to_csv(out / "decomposition.csv", index=False)
    analysis.variance_explained(data).to_csv(out / "variance_explained.csv")
    analysis.expense_mix(data).to_csv(out / "expense_mix.csv")
    plots.plot_index(index, out / "index.png", args.cohort)
    plots.plot_decomposition(effects, out / "decomposition.png", args.cohort)

    print(summary.T.to_string(float_format=lambda v: f"{v:,.2f}"))
    print(index.round(0).to_string())
    print(analysis.variance_explained(data).round(3).to_string())
    full = effects[(effects["start"] == config.YEARS[0]) & (effects["end"] == config.YEARS[-1])]
    print(full.pivot(index="factor", columns="group", values="share_of_change").round(3).to_string())
    print(f"outputs in {out}")


if __name__ == "__main__":
    main()
