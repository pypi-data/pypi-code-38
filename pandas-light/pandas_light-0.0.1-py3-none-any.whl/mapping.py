import pandas as pd
from .insert import *


def vmap(df_base, df_ref, on=None, right_on=None, take=None, after=None):
    """Import lookup columns from a reference df.

    Args:
        df_base (DataFrame): The self.
        df_ref (DataFrame): The reference datarframe containing the columns to lookup and import.
        on (str or [str], optional): Key columns in df_base. Defaults to intersection of columns in both df.
        right_on (str or [str], optional): Key columns in df_ref. Defaults to the same as on.
        take (str or [str], optional): Columns to be imported from df_ref. Defaults to all non-key columns.
        after (str, optional): Insert after which column in df_base. Defaults to the last key column.

    Returns:
        DataFrame: The modified dataframe. No side-effect.
    """
    def process_arg(x, default):
        if x is None:
            return default
        elif isinstance(x, str):
            return [x]
        else:
            return x
    on = process_arg(on, list(set(df_base.columns) & set(df_ref.columns)))
    right_on = process_arg(right_on, on)
    take = process_arg(take, [col for col in df_ref.columns if (col not in right_on)])

    base = df_base.copy()
    ref = df_ref[right_on + take].copy()

    ref = ref.rename(columns=dict(zip(right_on, on)))
    df_new = base[on].merge(ref, how='left', on=on)
    df_new.index = base.index
    df_new = df_new[take]
    after = after or on[-1]
    for column in list(reversed(df_new.columns)):
        base.pipe(insert_after, df_new[column], after)
    return base
