import pandas as pd
import numpy as np
from typing import List
from .globals import *
from .estmode import EstMode

def most_related_columns(df: pd.DataFrame, target: str, number: int) -> List[str]:
    return list(df.corr()[target].abs().sort_values(ascending=False)[:number].index.values)

def all_cols_except(df: pd.DataFrame, targets: List[str]) -> List[str]:
    return list(set(df.columns.values) - set(targets))

def dummify(df, cols: List[str]):
        onehot = pd.get_dummies(df[cols])
        confirm_all_dropped(onehot, cols)
        df.drop(cols, axis=1, inplace=True)
        for col in onehot:
                df[col] = onehot[col]

def confirm_all_dropped(df: pd.DataFrame, cols: List[str]):
        dropped = set(cols) - set(df.columns.values)
        if len(dropped) < len(cols):
            raise ValueError("the following columns were not one-hot encoded: ", *set(cols) - dropped)

def categorize_all_strings(df: pd.DataFrame):
        for col in cat_cols(df):
                df[col] = df[col].astype('category').cat.codes

def fill_ordinal_na(df: pd.DataFrame):
        for col in  all_cols_except(df, cat_cols(df)):
                assert ORDINAL_BAD_VALUE not in df[col].values, f"column {col} already contains {ORDINAL_BAD_VALUE}" 
                df[col].fillna(ORDINAL_BAD_VALUE, inplace=True)

# encode_string_na encodes all string columns as numbers and
# replaces all na values in non-string columns with an anomalous
# intger value. The dataset can now be fit to a sklearn 
# estimator.
def encode_string_na(df: pd.DataFrame):
        categorize_all_strings(df)
        fill_ordinal_na(df)

def cls_impute(est, df: pd.DataFrame, cols: List[str]):
        est_impute(est, df, cols, EstMode.classify)

def reg_impute(est, df: pd.DataFrame, cols: List[str]):
        est_impute(est, df, cols, EstMode.regress)

def est_impute(est, df: pd.DataFrame, cols: List[str], mode: EstMode):
        if mode == EstMode.classify:
                bad_val = CATEGORICAL_BAD_VALUE
        else:
                bad_val = ORDINAL_BAD_VALUE

        for col in cols:
                features = all_cols_except(df, [col])

                # when training the model we remove tows where the
                # target column has a bad value (otherwise the 
                # classifier would sometimes predict bad values).
                clean_frame =  df.loc[df[col] != bad_val, :]
                est.fit(
                        clean_frame[features], 
                        clean_frame[col]
                )
                preds = est.predict(df[features])
                df.loc[df[col] == bad_val, col] = np.extract((df[col] == bad_val).values, preds)

def cat_cols(df: pd.DataFrame) -> List[str]:
        return df.select_dtypes(["category", "object"]).columns.values