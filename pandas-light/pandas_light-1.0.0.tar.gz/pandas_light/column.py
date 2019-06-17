import pandas as pd
import pandas_flavor as pf
from .tool import *


@pf.register_dataframe_method
def move_column(df, move, after=None, before=None):
    """Move a specific column to another position. Not Inplace.

    Args:
        move (str or [str]): Column(s) to move.
        after (str, optional): Move to after which column. Defaults to the last column.
        before (str, optional): Move to before which column. Override after if provided. Defaults to none.
    """
    move = str_listify(move)
    c = list_except(df.columns, move)
    if before is None:
        after = after or c[-1]
        i = c.index(after) + 1
        c[i:i] = move
        return df[c]
    else:
        i = c.index(before)
        c[i:i] = move
        return df[c]


@pf.register_dataframe_method
def drop_column(df, columns):
    """Drop specified columns.

    Args:
        columns (str or [str]): Column(s) to drop.
    """
    columns = str_listify(columns)
    return df.drop(columns=columns)


@pf.register_dataframe_method
def add_column(df, name, series):
    """Add a new column.

    Args:
        name (str): The name of the new column.
        series (Series): The Series object to add.
    """
    if name in df.columns:
        raise Exception('Column name "' + name + '" already exist!')
    ndf = df.copy()
    ndf[name] = series
    return ndf


@pf.register_dataframe_method
def rename_column(df, old, new):
    """[summary]

    Args:
        old (str or [str]): The old column name(s).
        new (str or [str]): The new column name(s).
    """
    old = str_listify(old)
    new = str_listify(new)
    return df.rename(columns=dict(zip(old, new)))
