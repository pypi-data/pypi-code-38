import pandas as pd
import numpy as np
from typing import List, Dict
from .globals import *
from .estmode import EstMode
from pandas.api.types import is_string_dtype, is_numeric_dtype

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

# set_true_na replaces all the na values in the given columns with 
# 0 if the column is ordinal, or "unknown" if the column is an object.
# The idea is that NA values for these values means that any value
# would be nonsensical. Passing in the names of categorical columns
# will cause errors to be thrown.
def set_true_na(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                assert df[col].dtype.name != "category", f"column {col} was categorical, cannot set true NA values on it"
                if is_string_dtype(df[col]):
                        assert UNKNOWN_STR_VAL not in df[col].unique(), f"column {col} already contains value {UNKNOWN_STR_VAL}."
                        df[col].fillna(UNKNOWN_STR_VAL, inplace=True)
                else:
                        df[col].fillna(UNKNOWN_NUM_VAL, inplace=True)

def convert_to_cat_codes(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                df[col] = df[col].astype('category').cat.codes

def fill_ordinal_na(df: pd.DataFrame, cols: List[str]):
        for col in cols:
                assert ORDINAL_BAD_VALUE not in df[col].unique(), f"column {col} already contains {ORDINAL_BAD_VALUE}" 
                df[col].fillna(ORDINAL_BAD_VALUE, inplace=True)

def encode_to_int(df: pd.DataFrame, encoding: Dict[str, Dict[str, int]]):
        df.replace(encoding, inplace=True)
        for col in encoding.keys():
                df[col].fillna(-1, inplace=True)
                df[col] = df[col].astype("int8")

def cls_impute(est, df: pd.DataFrame, cols: List[str]):
        est_impute(est, df, cols, EstMode.classify)

def reg_impute(est, df: pd.DataFrame, cols: List[str]):
        est_impute(est, df, cols, EstMode.regress)

# est_impute replaces all bad values with the given 
# classifier's predictions. It is assmed that the bad values
# have already been replaced with certain integers.
def est_impute(est, df: pd.DataFrame, cols: List[str], mode: EstMode):
        if mode == EstMode.classify:
                bad_val = CATEGORICAL_BAD_VALUE
        else:
                bad_val = ORDINAL_BAD_VALUE

        for col in cols:
                features = all_cols_except(df, [col])

                # when training the model we remove rows where the
                # target column has a bad value (since these are 
                # the row's we're trying to predict for). 
                clean_frame =  df.loc[df[col] != bad_val, :]
                est.fit(
                        clean_frame[features], 
                        clean_frame[col]
                )
                preds = est.predict(df[features])
                df.loc[df[col] == bad_val, col] = np.extract((df[col] == bad_val).values, preds)

def str_cols(df: pd.DataFrame) -> List[str]:
        return df.select_dtypes(["category", "object"]).columns.values

def int_cols(df: pd.DataFrame) -> List[str]:
        return all_cols_except(df, str_cols(df))

# used for viewing the results of a Sklearn CV searcher
# more easily.
def best_n_params(results, number):
    params = []
    scores = []
    all_ranks = list(results["rank_test_score"])
    all_params = results["params"]
    all_scores = results["mean_test_score"]
    
    for i in range(number):
        if i+1 in all_ranks:
                indices = [index for index, rank in enumerate(all_ranks) if rank == i+1]
                for index in indices:
                        params.append(all_params[index])
                        scores.append(all_scores[index])
    return (params, scores)