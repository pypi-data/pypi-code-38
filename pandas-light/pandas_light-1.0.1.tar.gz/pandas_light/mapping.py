import pandas as pd
from .insert import *
import pandas_flavor as pf
from .tool import *


@pf.register_dataframe_method
def vmap(df, df_ref, on=None, right_on=None, take=None, after=None):
    """Import lookup columns from a reference df. Not inplace.

    Args:
        df_ref (DataFrame): The reference datarframe containing the columns to lookup and import.
        on (str or [str], optional): Key columns in df_base. Defaults to intersection of columns in both df.
        right_on (str or [str], optional): Key columns in df_ref. Defaults to the same as on.
        take (str or [str], optional): Columns to be imported from df_ref. Defaults to all non-key columns.
        after (str, optional): Insert after which column in df_base. Defaults to the last key column.
    """
    def process_arg(x, default):
        if x is None:
            return default
        elif isinstance(x, str):
            return [x]
        else:
            return x
    on = process_arg(on, list(df.columns & df_ref.columns))
    right_on = process_arg(right_on, on)
    take = process_arg(take, list_except(df_ref.columns, right_on))

    base = df.copy()
    ref = df_ref[right_on + take].copy()

    ref = ref.rename(columns=dict(zip(right_on, on)))
    ndf = base[on].merge(ref, how='left', on=on)
    ndf.index = base.index
    ndf = ndf[take]
    after = after or on[-1]
    i = list(base.columns).index(after) + 1
    for column in list(reversed(ndf.columns)):
        base.insert(i, column, ndf[column])
    return base
