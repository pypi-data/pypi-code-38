import pandas as pd


def insert_after(df, series, after, column_label='new_column'):
    """Insert a column after the specified column.

    Args:
        df (DataFrame): Self.
        series (Series): The column object to insert.
        after (str): After which column.
        column_label (str, optional): The name of the inserted column. Defaults to series name or 'new_column'.
    """
    if column_label == 'new_column' and series.name != None:
        column_label = series.name
    i = list(df.columns).index(after) + 1
    df.insert(i, column_label, series)


def insert_before(df, series, before, column_label='new_column'):
    """Insert a column before the specified column.

    Args:
        df (DataFrame): Self.
        series (Series): The column object to insert.
        before (str): Before which column.
        column_label (str, optional): The name of the inserted column. Defaults to series name or 'new_column'.
    """
    if column_label == 'new_column' and series.name != None:
        column_label = series.name
    i = list(df.columns).index(before)
    df.insert(i, column_label, series)
