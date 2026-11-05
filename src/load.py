"""Read the raw HCAI files and pivots into one long frame per source."""
import re
import warnings

import pandas as pd

import config


def normalize_columns(df):
    cols = [re.sub(r"\s+", "", str(c)).upper() for c in df.columns]
    return df.set_axis([config.COLUMN_ALIASES.get(c, c) for c in cols], axis=1)


def read_table(path, **kwargs):
    if path.suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pd.read_excel(path, **kwargs)


def load_raw():
    needed = config.ID_COLS + config.DATE_COLS + config.FLOW_COLS
    frames = []
    for year, name in config.RAW_FILES.items():
        df = normalize_columns(read_table(config.RAW_DIR / name))
        missing = sorted(set(needed) - set(df.columns))
        if missing:
            print(f"WARNING {year}: missing columns {missing}")
        frames.append(df.reindex(columns=needed).assign(FILE_YEAR=year))
    return pd.concat(frames, ignore_index=True)


def load_pivots():
    frames = []
    for year, name in config.PIVOT_FILES.items():
        df = normalize_columns(
            read_table(config.PIVOT_DIR / name, sheet_name=config.PIVOT_SHEET)
        )
        df = df[["FAC_NO", "DAY_PER", "ADJPATDAYS"]].assign(YEAR=year)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
