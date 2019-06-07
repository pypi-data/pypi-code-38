import pandas as pd


def gather(df, columns, var_name='variable', value_name='value'):
    """Gather the columns into rows. Equivalent to df.melt but directly pass value columns.

    Args:
        df (DataFrame): Self.
        columns (str or [str]): The column(s) to gather.
        var_name (str, optional): The column name for the variables (original column names). Defaults to 'variable'.
        value_name (str, optional): The column name for the values (original column content). Defaults to 'value'.

    Returns:
        DataFrame: The modified dataframe. No side-effect.
    """
    if isinstance(columns, str):
        columns = [columns]
    id_cols = [x for x in df.columns if (x not in columns)]
    return df.melt(id_vars=id_cols, var_name=var_name, value_name=value_name)


def spread(df, var_column, value_column):
    """Spread the rows into columns. Equivalent to df.pivot_table and then flatten index.
    If there are duplicated values, the first one is taken.

    Args:
        df (DataFrame): Self.
        var_column (str): The resulting columns' names.
        value_column (str): The resulting columns' values.

    Returns:
        DateFrame: The modified dataframe. No side-effect.
    """
    index_columns = [x for x in df.columns if (x not in [var_column, value_column])]
    p = df.pivot_table(index=index_columns, columns=var_column, values=value_column, aggfunc='first')
    p = p.reset_index()
    p.columns.name = None
    return p
