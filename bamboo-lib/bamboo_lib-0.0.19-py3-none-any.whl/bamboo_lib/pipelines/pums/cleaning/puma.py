from bamboo_lib.logger import logger
from bamboo_lib.pipelines.pums.cleaning.puma_helper import update_puma

PUMA = 'puma'
PUMA00 = 'puma00'
PUMA10 = 'puma10'


def _make_geo_id(df, on_col):
    df[on_col] = df[on_col].astype(int)
    mycond = df[on_col] != -9
    df.loc[mycond, on_col] = df.loc[mycond, 'st'].astype(str).str.zfill(2) + df.loc[mycond, on_col].astype(str).str.zfill(5)
    df.loc[~mycond, on_col] = None
    return df


def puma_cleaning(df, year, estimate):
    logger.info("Cleaning PUMAs...")

    if "puma00" in df.columns and "puma10" in df.columns:
        df = _make_geo_id(df, PUMA00)
        df = _make_geo_id(df, PUMA10)
        # apply crosswalk and normalize column name
        df = update_puma(df, PUMA00, True)
        df[PUMA] = '79500US' + df[PUMA]
    else:
        df[PUMA] = "79500US" + df.st + df[PUMA]

    return df
