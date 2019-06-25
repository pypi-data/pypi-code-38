# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pyspark.sql.dataframe import DataFrame
from pyspark.sql.utils import AnalysisException


def has_column(df: DataFrame, col: str) -> bool:
    """
    :param df: Spark DataFrame
    :param col: Column name

    :return: True if the DataFrame has the column "col" else False
    """
    try:
        df[col]
        return True
    except AnalysisException:
        return False
