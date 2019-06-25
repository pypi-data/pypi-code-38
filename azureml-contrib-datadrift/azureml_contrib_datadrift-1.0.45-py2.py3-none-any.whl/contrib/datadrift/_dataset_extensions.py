# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Dataset extensions."""

import numpy as np
import pandas as pd

from ._logging._telemetry_logger import _TelemetryLogger
from azureml.contrib.datadrift import _datadiff as dd
from azureml.contrib.datadrift._utils import pdutils
from azureml.contrib.datadrift._utils.constants import COLUMN_NAME, \
    METRIC_TYPE, METRIC_TYPE_DATASET, METRIC_TYPE_COLUMN, \
    OUTPUT_METRIC_DRIFT_COEFFICIENT

dataset_logger = _TelemetryLogger.get_telemetry_logger(__name__)


def detect_drift(self, rhs_dataset):
    """
    Calculate drift between the given two datasets.

    :param rhs_dataset: RHS dataset
    :type rhs_dataset: Dataset
    :return: Drift of the two given datasets, mismatched columns in both two datasets.
    :rtype: azureml.contrib.datadrift._datadiff.Metric, list(), list()
    """
    ds1 = self.to_pandas_dataframe()
    ds2 = rhs_dataset.to_pandas_dataframe()
    metrics, ds_model, ds1_mismatch, ds2_mismatch = run_datadiff(ds1, ds2, dataset_logger)

    # re-org metrics accrording to design doc:
    # https://microsoft.sharepoint.com/:w:/t/ThirdPartyDataSet/EQ_fU0UooQFDkufumwAyUnkB3JZyKBJgeJVoXeyCCWFKuw?e=LUmO3O
    # 1. get all columns
    columns = []
    for m in metrics:
        if m.extended_properties[METRIC_TYPE] == METRIC_TYPE_COLUMN:
            columns.append(m.extended_properties[COLUMN_NAME])
    # 2. re-org output per column
    contents = {}
    for m in metrics:
        if m.extended_properties[METRIC_TYPE] == METRIC_TYPE_DATASET \
                and m.name == OUTPUT_METRIC_DRIFT_COEFFICIENT:
            contents[OUTPUT_METRIC_DRIFT_COEFFICIENT] = m.value
        if m.extended_properties[METRIC_TYPE] == METRIC_TYPE_COLUMN:
            current_column = m.extended_properties[COLUMN_NAME]
            if current_column not in contents:
                contents[current_column] = {}
            item_name = m.name
            if item_name not in contents[current_column]:
                contents[current_column][item_name] = {}
            contents[current_column][item_name] = m.value

    return contents, ds1_mismatch, ds2_mismatch


def get_distributions(pd_dataset, decimal=3):
    distributions = []

    for column in pd_dataset:
        if pd.api.types.is_numeric_dtype(pd_dataset[column].dtype):
            binlabel, weight = np.unique(np.around(pd_dataset[column].values, decimal), return_counts=True)
            distributions.append(dd.Distribution(column, binlabel, weight))

    return distributions


def run_datadiff(base_ds, diff_ds, logger, include_columns=None):
    common_columns = set(base_ds.columns & diff_ds.columns)

    if include_columns is None or len(include_columns) == 0:
        columns = list(common_columns)
        logger.info("Common columns:{}".format(", ".join(columns)),
                    extra={'properties':
                           {"common_col_counts": len(columns)}
                           })
    else:
        columns = list(set(include_columns) & common_columns)
        logger.info("Whitelisted columns:{}".format(", ".join(include_columns)),
                    extra={'properties':
                           {"whitelist_col_counts": len(include_columns)}
                           })
        missing_columns = set(include_columns) - set(columns)
        if len(missing_columns) != 0:
            logger.warning("Missing columns:{}".format(", ".join(missing_columns)),
                           extra={'properties':
                                  {"Missing_col_counts": len(missing_columns)}
                                  })

    base_processed, diff_processed = get_preprocessed_dfs(
        base_ds[columns], diff_ds[columns], logger)

    assert len(base_processed.columns) != 0, "No columns are available for diff calculation."

    logger.info("Columns eligible for diff: {}".format(", ".join(base_processed.columns)),
                extra={'properties':
                       {"diff_col_counts": len(base_processed.columns)}
                       })

    base_distribution = get_distributions(base_processed)
    diff_distribution = get_distributions(diff_processed)
    ddo = dd.DataDiff(base_processed, diff_processed, base_distribution, diff_distribution)
    metrics = ddo.run()
    ds_model = ddo.model_dict["ds_model"]

    base_columns_mismatched = list(filter(lambda c: c not in columns, base_ds.columns))
    diff_columns_mismatched = list(filter(lambda c: c not in columns, diff_ds.columns))

    return metrics, ds_model, base_columns_mismatched, diff_columns_mismatched


def get_preprocessed_dfs(base, diff, logger):
    common_columns = base.columns & diff.columns

    dfsummaries_base = pdutils.get_pandas_df_summary(base[common_columns])
    dfsummaries_diff = pdutils.get_pandas_df_summary(diff[common_columns])

    columns_to_drop = list(set(pdutils.get_inferred_drop_columns(dfsummaries_base)).union(
        set(pdutils.get_inferred_drop_columns(dfsummaries_diff))))

    base_fillna_columns = pdutils.get_inferred_fillna_columns(dfsummaries_base)
    diff_fillna_columns = pdutils.get_inferred_fillna_columns(dfsummaries_diff)

    common_columns_filtered = list(set(common_columns) - set(columns_to_drop))

    categorical_columns = list(set(pdutils.get_inferred_categorical_columns(dfsummaries_base)).intersection(
        common_columns_filtered))

    logger.info("Columns to be dropped from comparision due to high invalid "
                "value counts from either or both of datasets: {}"
                .format(", ".join(columns_to_drop)),
                extra={'properties':
                       {"drop_col_counts": len(columns_to_drop)}
                       })

    logger.info("Columns treated as categorical columns base on baseline dataset: {}"
                .format(", ".join(categorical_columns)),
                extra={'properties':
                       {"cat_col_counts": len(categorical_columns)}
                       })

    logger.info("Columns treated with fillna with mean for base dataset: {}"
                .format(", ".join(base_fillna_columns)),
                extra={'properties':
                       {"base_fillna_col_counts": len(base_fillna_columns)}
                       })

    logger.info("Columns with non-zero null values but under threshold: {}"
                .format(", ".join(diff_fillna_columns)),
                extra={'properties':
                       {"diff_fillna_col_counts": len(diff_fillna_columns)}
                       })

    for c in categorical_columns:
        base[c] = base[c].fillna(value="__null__")
        diff[c] = diff[c].fillna(value="__null__")
        common_cats = list(set(np.concatenate((base[c].unique(), diff[c].unique()))))
        cat_type = pd.api.types.CategoricalDtype(categories=common_cats)
        base[c] = base[c].astype(cat_type)
        diff[c] = diff[c].astype(cat_type)

    base[base_fillna_columns] = base[base_fillna_columns].fillna(base[base_fillna_columns].mean())
    # diff fillna with mean using baseline dataset to avoid introducing highly distinguishable values.
    # This is intended and not a bug.
    diff[diff_fillna_columns] = diff[diff_fillna_columns].fillna(base[diff_fillna_columns].mean())

    return base[common_columns_filtered], diff[common_columns_filtered]
