import os
import numpy as np
import pandas as pd
from bamboo_lib.logger import logger
from numpy.random import choice

PUMA = 'puma'
PUMA00 = 'puma00'
PUMA10 = 'puma10'
KATRINA_PUMA = '2277777'
UNKNOWN_LIST = ['XXXXX', None, np.nan, -9]
COL_RATE = "Total Conversion Rate"

RATE_CONVERTER = 'pPUMA00_Pop10'

data_dir = os.path.dirname(__file__)


def get_path(target):
    return os.path.join(data_dir, target)


converters = {"State00": str, "State10": str, PUMA00: str, PUMA10: str}
puma_map = pd.read_excel(get_path('data/PUMA2000_PUMA2010_crosswalk.xls'), converters=converters)[["State00", "State10", PUMA00, PUMA10, "pPUMA00_Pop10"]]
puma_map[PUMA00] = puma_map["State00"] + puma_map[PUMA00]
puma_map[PUMA10] = puma_map["State10"] + puma_map[PUMA10]
puma_map = puma_map.drop(["State00", "State10"], axis=1)
puma_map[RATE_CONVERTER] = puma_map[RATE_CONVERTER] / 100.00
puma_map = puma_map.set_index(PUMA00)


def diluter_update_puma(df, on_col, has_puma10=False):
    '''This verison will distribute the person weight'''
    df = pd.merge(puma_map, df, left_on=PUMA00, right_on=on_col, how="right")
    df.drop([PUMA00], axis=1, inplace=True)
    # df.rename(columns={PUMA10: PUMA}, inplace=True)

    # Dilute person weight values by RATE_CONVERTER
    for col in df.columns:
        if "pwgtp" in col.lower():
            df.loc[df['puma10_x'].notnull(), col] = df.loc[df['puma10_x'].notnull(), col] * df[RATE_CONVERTER]

    df.loc[df['puma10_x'].notnull(), PUMA] = df['puma10_x']
    df.loc[df['puma10_y'].notnull(), PUMA] = df['puma10_y']
    df.drop(["puma10_x", "puma10_y", RATE_CONVERTER], axis=1, inplace=True)
    return df


def randomizer(code):
    if code in UNKNOWN_LIST:
        raise Exception("INVALID PUMA! UNKNOWN!")
    if code == KATRINA_PUMA:
        return KATRINA_PUMA

    tmpdf = puma_map.ix[code]

    if isinstance(tmpdf, pd.Series):
        return tmpdf[PUMA10]

    # print code
    # normalize tmpdf[RATE_CONVERTER].values
    tmp_arr = tmpdf[RATE_CONVERTER].values
    tot_sum = sum(tmp_arr)
    p_vals = [1.0 * p / tot_sum for p in tmp_arr]
    selected_idx = choice(range(len(tmpdf)), p=p_vals)
    return tmpdf.iloc[selected_idx][PUMA10]


def update_puma(df, on_col, has_puma10=False):
    to_drop = [on_col]

    df.loc[df[on_col].notnull(), on_col] = df.loc[df[on_col].notnull(), on_col].apply(randomizer)
    df.loc[df[on_col].notnull(), PUMA] = df.loc[df[on_col].notnull(), on_col]
    df.loc[df[PUMA10].notnull(), PUMA] = df.loc[df[PUMA10].notnull(), PUMA10]
    to_drop.append(PUMA10)
    df.drop(to_drop, axis=1, inplace=True)
    return df


if __name__ == '__main__':
    moi = pd.DataFrame({"puma10": [None, "2500506"], "puma00": ["5100600", None], "PWGTP": [100, 200], "PWGTP1": [100, 200], "PWGTP2": [60, 200]})
    print(update_puma(moi, "puma00"))
