# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Define runtime environment classes."""

from multimethods import multimethod
from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame


class RuntimeEnv(object):
    """Base class definition of runtime environment."""


class SparkEnv(RuntimeEnv):
    """Class definition of SparkEnv."""


class PandasEnv(RuntimeEnv):
    """Class definition of PandasEnv."""


@multimethod(SparkDataFrame)
def get_environ(data):
    """Get runtime environment of spark."""
    return SparkEnv()


@multimethod(PdDataFrame)
def get_environ(data):
    """Get runtime environment of pandas."""
    return PandasEnv()
