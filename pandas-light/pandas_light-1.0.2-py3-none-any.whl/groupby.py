import pandas as pd
import pandas_flavor as pf


@pf.register_dataframe_method
def summarize(df,groupby,names,funcs):
    """Summarize a DataFrame after a groupby.
    
    Args:
        groupby (str or [str]): Name(s) of the groupby column(s).
        names ([str]): Names of the resulting columns.
        funcs ([func]): Functions to apply to sub-DataFrame.
    """
    if len(names) != len(funcs):
        raise Exception('len(names) is equal not len(funcs) in DataFrame.summarize!')
    def afunc(d):
        values = [func(d) for func in funcs]
        return pd.Series(values,names)
    ndf = df.groupby(groupby).apply(afunc)
    ndf = ndf[names]
    ndf = ndf.reset_index()
    return ndf