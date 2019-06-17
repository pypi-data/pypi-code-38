import pandas as pd
import numpy as np
import pandas_flavor as pf

@pf.register_series_method
def fractionize(series):
    """Divide each element by the sum of the series. Not Inplace.
    """
    sum = series.sum()
    return series / sum

@pf.register_series_method
def normalize(series):
    """Divide each element by the max of the series. Not Inplace.
    """
    max = series.max()
    return series / max

@pf.register_series_method
def unitarize(series):
    """Linearly scale the series so min -> 0 and max -> 1. Not Inplace.
    """
    min = series.min()
    max = series.max()
    return (series - min) / (max - min)

@pf.register_series_method
def zscore(series):
    """Zscoring the series. Not Inplace.
    """
    mean = series.mean()
    sd = np.std(series)
    return (series - mean) / sd

@pf.register_series_method
def list_contains(series, element):
    """Whether each of the lists in Series contains the specified element.
    
    Args:
        element (object): What to contain.
    """
    return series.map(lambda x: element in x if x is not None else None)

@pf.register_series_method
def list_join(series, delimiter):
    """Join each of the lists in Series into a string.
    
    Args:
        delimiter (str): The delimiter used in the join.
    """
    return series.map(lambda x: delimiter.join(x) if x is not None else None)


@pf.register_series_method
def only(series):
    """Return the only element in the Series. Raise Exception otherwise.
    """
    if series.size == 0:
        raise Exception('The Series has no element!')
    if series.size > 1:
        raise Exception('The Series has more than one element!')
    return series.iloc[0]


@pf.register_series_method
def only_default(series,default = None):
    """Return the only element in the Series. Return default otherwise.
    
    Args:
        default (any, optional): Defaults to None.
    """
    if series.size != 1:
        return default
    return series.iloc[0]


@pf.register_dataframe_method
def show(df):
    """Print the DataFrame.
    """
    print(df.to_string())


@pf.register_dataframe_method
def zipdict(df,key_column,value_column, unique_key=True):
    """Return a Dict from two columns of the DataFrame.
    
    Args:
        key_column (str): Name of key column.
        value_column (str): Name of value column.
        unique_key (bool): Whether the key_column is unique. If no, multiple values are stored in a list.
    """
    if unique_key:
        if not df[key_column].is_unique:
            raise Exception('key_column has duplicate element!')
        return dict(zip(df[key_column],df[value_column]))
    if not unique_key:
        dct = {}
        for k,v in zip(df[key_column],df[value_column]):
            dct.setdefault(k, []).append(v)
        return dct
        

