import pandas as pd
import pandas_flavor as pf
from .tool import *

@pf.register_dataframe_method
def gather(df, columns, var_name='variable', value_name='value'):
    """Gather the columns into rows. Equivalent to df.melt but directly pass value columns. Not inplace.

    Args:
        columns (str or [str]): The column(s) to gather.
        var_name (str, optional): The column name for the variables (original column names). Defaults to 'variable'.
        value_name (str, optional): The column name for the values (original column content). Defaults to 'value'.
    """
    columns = str_listify(columns)
    id_cols = list_except(df.columns, columns)
    return df.melt(id_vars=id_cols, var_name=var_name, value_name=value_name)


@pf.register_dataframe_method
def spread(df, var_column, value_column):
    """Spread the rows into columns. Equivalent to df.pivot_table and then flatten index. Not Inplace.
    If there are duplicated values, the first one is taken.

    Args:
        var_column (str): The resulting columns' names.
        value_column (str): The resulting columns' values.
    """
    index_columns = list_except(df.columns, [var_column, value_column])
    p = df.pivot_table(index=index_columns, columns=var_column, values=value_column, aggfunc='first')
    p = p.reset_index()
    p.columns.name = None
    return p
