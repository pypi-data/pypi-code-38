from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from category_encoders import OrdinalEncoder, OneHotEncoder, BinaryEncoder

from bamboos.utils.dataframe import insert_df


def fit_label(input_df, cols, na_value=None):
    df = input_df.copy()

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    encoder = OrdinalEncoder(cols)
    encoder = encoder.fit(df)
    for idx in range(len(encoder.mapping)):
        encoder.mapping[idx]["mapping"].loc[np.nan] = -2

    result_df = encoder.transform(df)

    for col in cols:
        result_df[col] = result_df[col].replace({-1: 0, -2: 0})
        result_df[col] = result_df[col].astype(int)

    model = {"encoder": encoder, "cols": cols, "na_value": na_value}
    return result_df, model


def transform_label(input_df, model):
    df = input_df.copy()

    encoder = model["encoder"]
    cols = model["cols"]
    na_value = model["na_value"]

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    result_df = encoder.transform(df)

    for col in cols:
        result_df[col] = result_df[col].replace({-1: 0, -2: 0})
        result_df[col] = result_df[col].astype(int)

    return result_df


def fit_onehot(input_df, cols, na_value=None):
    df = input_df.copy()

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    drop_cols = ["{}_nan".format(col) for col in cols]

    encoder = OneHotEncoder(cols=cols, use_cat_names=True)
    encoder = encoder.fit(df)

    result_df = encoder.transform(df)

    for drop_col in drop_cols:
        if drop_col in result_df.columns:
            result_df = result_df.drop(columns=[drop_col])

    model = {"encoder": encoder, "cols": cols, "na_value": na_value, "drop_cols": drop_cols}
    return result_df, model


def transform_onehot(input_df, model):
    df = input_df.copy()

    encoder = model["encoder"]
    cols = model["cols"]
    na_value = model["na_value"]
    drop_cols = model["drop_cols"]

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    result_df = encoder.transform(df)

    for drop_col in drop_cols:
        if drop_col in result_df.columns:
            result_df = result_df.drop(columns=[drop_col])

    return result_df


def fit_binary(input_df, cols, na_value=None):
    df = input_df.copy()

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    encoder = BinaryEncoder(cols=cols, drop_invariant=True)
    encoder = encoder.fit(df)
    for idx in range(len(encoder.base_n_encoder.ordinal_encoder.mapping)):
        encoder.base_n_encoder.ordinal_encoder.mapping[idx]["mapping"].loc[np.nan] = -2

    result_df = encoder.transform(df)

    model = {"encoder": encoder, "cols": cols, "na_value": na_value}
    return result_df, model


def transform_binary(input_df, model):
    df = input_df.copy()

    encoder = model["encoder"]
    cols = model["cols"]
    na_value = model["na_value"]

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    result_df = encoder.transform(df)

    return result_df


def fit_categorical(input_df, cols, na_value=None, max_onehot=10, max_binary=1000):
    df = input_df.copy()

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    onehot_cols = []
    label_cols = []
    binary_cols = []

    for col in cols:
        col_values = df[col].values
        cardinality = len(np.unique(col_values[~pd.isnull(col_values)]))
        if cardinality < max_onehot:
            onehot_cols.append(col)
        elif cardinality < max_binary:
            label_cols.append(col)
        else:
            binary_cols.append(col)

    df, onehot_model = fit_onehot(df, onehot_cols, na_value)
    df, label_model = fit_label(df, label_cols, na_value)
    result_df, binary_model = fit_binary(df, binary_cols, na_value)

    model = {
        "onehot_model": onehot_model,
        "label_model": label_model,
        "binary_model": binary_model,
        "onehot_cols": onehot_cols,
        "label_cols": label_cols,
        "binary_cols": binary_cols,
        "cols": cols,
        "na_value": na_value,
        "max_onehot": max_onehot,
        "max_binary": max_binary,
    }
    return result_df, model


def transform_categorical(input_df, model):
    df = input_df.copy()

    onehot_model = model["onehot_model"]
    label_model = model["label_model"]
    binary_model = model["binary_model"]
    cols = model["cols"]
    na_value = model["na_value"]

    if na_value is not None:
        for col in cols:
            df[col] = df[col].replace({na_value: np.nan})

    df = transform_onehot(df, onehot_model)
    df = transform_label(df, label_model)
    result_df = transform_binary(df, binary_model)

    return result_df


def fit_stats(
    input_df: pd.DataFrame, stat_cols: List[str], target_cols: List[str], metric_cols: Any = None
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, pd.DataFrame]]]:
    for col_name in ["stat_cols", "target_cols", "metric_cols", "default"]:
        assert col_name not in stat_cols, "Please don't use {} as a Stats column name".format(col_name)
        assert col_name not in target_cols, "Please don't use {} as a Target column name".format(col_name)
    df = input_df.copy()

    df = df[stat_cols + target_cols]
    if not metric_cols:
        metric_cols = ["mean", "median", "std", "min", "max"]
    if isinstance(metric_cols, dict):
        assert set(stat_cols) == set(metric_cols)

    stats_encoder = dict()  # type: dict
    for stat_col in stat_cols:
        stats_encoder[stat_col] = dict()
        if isinstance(metric_cols, dict):
            stat_metric_cols = metric_cols[stat_col]
        else:
            stat_metric_cols = metric_cols
        for target_col in target_cols:
            agg_df = df.groupby(stat_col)[target_col].agg(stat_metric_cols).reset_index()

            default_df = pd.DataFrame([df[target_col].agg(stat_metric_cols)]).reset_index(drop=True)
            default_df[stat_col] = "default"
            default_df = default_df[[stat_col] + stat_metric_cols]

            full_agg_df = agg_df.append(default_df)

            stat_colname = ["{}_{}_{}".format(stat_col, target_col, metrics_col) for metrics_col in stat_metric_cols]
            full_agg_df.columns = [stat_col] + stat_colname
            stats_encoder[stat_col][target_col] = full_agg_df

    stats_encoder["stat_cols"] = stat_cols
    stats_encoder["target_cols"] = target_cols
    stats_encoder["metric_cols"] = metric_cols

    result_df = transform_stats(input_df, stats_encoder)
    return result_df, stats_encoder


def transform_stats(input_df: pd.DataFrame, stats_encoder_dict: Dict[str, Any]) -> pd.DataFrame:
    stat_cols = stats_encoder_dict["stat_cols"]
    target_cols = stats_encoder_dict["target_cols"]
    metric_cols = stats_encoder_dict["metric_cols"]
    result_df = input_df.copy()

    # pylint: disable=cell-var-from-loop
    for stat_col in stat_cols:
        if isinstance(metric_cols, dict):
            stat_metric_cols = metric_cols[stat_col]
        else:
            stat_metric_cols = metric_cols
        for target_col in target_cols[::-1]:
            stat_col_idx = result_df.columns.get_loc(stat_col) + 1
            stat_colname = ["{}_{}_{}".format(stat_col, target_col, metrics_col) for metrics_col in stat_metric_cols]

            small_df = result_df[[stat_col]].copy()
            small_df[stat_col] = small_df[stat_col].apply(
                lambda x: "default" if x not in stats_encoder_dict[stat_col][target_col][stat_col].tolist() else x
            )
            agg_df = small_df.merge(stats_encoder_dict[stat_col][target_col], how="left", on=stat_col, validate="m:1")[
                stat_colname
            ]
            result_df = insert_df(result_df, agg_df, stat_col_idx)
    return result_df
