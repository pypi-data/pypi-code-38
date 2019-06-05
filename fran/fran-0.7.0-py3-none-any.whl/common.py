import logging
from enum import IntEnum

import pandas as pd
import numpy as np

from fran.constants import FRAME_LEVEL


iinfo = np.iinfo(pd.Int64Dtype().numpy_dtype)


class Special(IntEnum):
    BEFORE = iinfo.min
    AFTER = iinfo.max

    @classmethod
    def has(cls, item):
        return item in list(cls)

    @classmethod
    def filter_out(cls, arr):
        arr = np.asarray(arr)
        arr[arr == Special.BEFORE] = np.nan
        arr[arr == Special.AFTER] = np.nan
        return arr


def not_frame_idx(n):
    return pd.isnull(n) or Special.has(n)


def parse_keys(s):
    d = dict()
    for pair in s.split(","):
        key, event = pair.split("=")
        event = event.strip()
        key = key.strip().lower()
        if len(key) > 1:
            raise ValueError("keys must be 1 character long")
        d[key] = event
    return d


def denan_df(df):
    df["start"] = [
        Special.BEFORE.value if pd.isnull(item) else item for item in df["start"]
    ]
    df["stop"] = [
        Special.AFTER.value if pd.isnull(item) else item for item in df["stop"]
    ]
    return df


def setup_logging(verbosity=0, logfile=None):
    verbosity = verbosity or 0
    logging.addLevelName(FRAME_LEVEL, "FRAME")
    levels = [logging.INFO, logging.DEBUG, FRAME_LEVEL, logging.NOTSET]
    v_idx = min(verbosity, len(levels) - 1)
    logging.captureWarnings(True)

    handlers = [logging.StreamHandler()]
    if logfile:
        handlers.append(logging.FileHandler(logfile))
    logging.basicConfig(level=levels[v_idx], handlers=handlers)


NAN_VALS = (
    "",
    "#N/A",
    "#N/A N/A",
    "#NA",
    "-1.#IND",
    "-1.#QNAN",
    "-NaN",
    "-nan",
    "1.#IND",
    "1.#QNAN",
    "N/A",
    "NA",
    "NULL",
    "NaN",
    "n/a",
    "nan",
    "null",
    "None",
)


def sanitise_note(item):
    try:
        if item not in NAN_VALS:
            return item.strip()
    except AttributeError:
        pass
    return ""


DTYPES = {
    "start": pd.Int64Dtype(),
    "stop": pd.Int64Dtype(),
    "key": str,
    "event": str,
    "note": sanitise_note,
}


def load_results(fpath):
    df = pd.read_csv(fpath, dtype=DTYPES, na_values=NAN_VALS)
    return df


def dump_results(df: pd.DataFrame, fpath=None, **kwargs):
    df_kwargs = {"index": False}
    df_kwargs.update(kwargs)
    return df.to_csv(fpath, **df_kwargs)


def df_to_str(df):
    return dump_results(df)


def fn_or(item, fn=int, default=None):
    try:
        return fn(item)
    except ValueError:
        return default
