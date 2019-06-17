import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def insert_after(df, series, after, column_label='new_column'):
    """Insert a column after the specified column. Not inplace.

    Args:
        series (Series): The Series object to insert.
        after (str): After which column.
        column_label (str, optional): The name of the inserted column. Defaults to series name or 'new_column'.
    """
    ndf = df.copy()
    if column_label == 'new_column' and series.name != None and series.name not in list(ndf.columns):
        column_label = series.name
    i = list(ndf.columns).index(after) + 1
    ndf.insert(i, column_label, series)
    return ndf

@pf.register_dataframe_method
def insert_before(df, series, before, column_label='new_column'):
    """Insert a column before the specified column. Not inplace.

    Args:
        series (Series): The Series object to insert.
        before (str): Before which column.
        column_label (str, optional): The name of the inserted column. Defaults to series name or 'new_column'.
    """
    ndf = df.copy()
    if column_label == 'new_column' and series.name != None and series.name not in list(ndf.columns):
        column_label = series.name
    i = list(ndf.columns).index(before)
    ndf.insert(i, column_label, series)
    return ndf
