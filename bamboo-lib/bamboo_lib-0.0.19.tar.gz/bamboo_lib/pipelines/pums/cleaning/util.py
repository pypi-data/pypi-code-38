
import numpy as np


def num_helper_1yr(df, col):
    df[col] = df[col].astype(str).str.lstrip('0')
    df[col] = df[col].astype(str).str.strip(' ')
    df.loc[df[col].astype(str).str.len() == 0, col] = 0
    df[col] = df[col].astype(float)
    return df


def num_helper_5yr(df, col):
    df[col] = df[col].astype(str).str.strip(' ')
    df.loc[df[col].astype(str).str.len() == 0, col] = 0
    df[col] = df[col].astype(float)
    return df


def num_helper(df, estimate, col):
    if estimate == 1:
        return num_helper_1yr(df, col)
    elif estimate == 5:
        return num_helper_5yr(df, col)
    raise ValueError("Invalid estimate", estimate)


def preclean_io_codes(df):
    to_replace = ["NAICSP02", "NAICSP07", "NAICSP12", "SOCP00", "SOCP10", "SOCP12"]
    for col in to_replace:
        col = col.lower()
        if col in df.columns:
            df.loc[df[col].isin(['N.A.////', 'N.A.//', 'N.A.']), col] = np.nan
    return df
