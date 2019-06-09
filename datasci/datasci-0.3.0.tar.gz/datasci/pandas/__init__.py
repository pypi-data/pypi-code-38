import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def drop_na_columns(df: pd.DataFrame, inplace=False) -> pd.DataFrame:
    """
    Simply calls df.dropna(axis='columns', how='all', ...)
    """
    return df.dropna(axis='columns', how='all', inplace=inplace)


def drop_uninformative_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns from df where values in all cells are identical.
    """
    # TODO: support DataFrames where df.columns is a MultiIndex
    for column in df.columns:
        series = df[column]
        series_iter = iter(df[column])
        try:
            exemplar = next(series_iter)
        except StopIteration:
            # no rows => nothing to check :|
            continue
        # nan is a special case, since np.nan != np.nan
        if series.dtype == np.float and np.isnan(exemplar) and all(np.isnan(item) for item in series_iter):
            logger.debug('Dropping column %r from DataFrame (every value is nan)', column)
            df = df.drop(column, axis='columns')
        elif all(item == exemplar for item in series_iter):
            logger.debug('Dropping column %r from DataFrame (every value = %r)', column, exemplar)
            df = df.drop(column, axis='columns')
    return df
