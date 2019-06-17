import pandas as pd
import pandas_flavor as pf
from .tool import *

@pf.register_dataframe_method
def filtrate(df,column,value):
    """Filtering. The column must be the specified value.
    
    Args:
        column (str): Column name.
        value (any): Filter value.
    """
    return df[df[column] == value]


@pf.register_dataframe_method
def filtrate_in(df,column,values_list):
    """Filtering. The column must be in the specified list of values.
    
    Args:
        column (str): Column name.
        values_list (list): The list of allowed values.
    """
    return df[df[column].isin(values_list)]


@pf.register_dataframe_method
def sieve(df,column,value):
    """Filtering. The column must NOT be the specified value.
    
    Args:
        column (str): Column name.
        value (any): Filter value.
    """
    return df[df[column] != value]

@pf.register_dataframe_method
def sieve_in(df,column,values_list):
    """Filtering. The column must NOT be in the specified list of values.
    
    Args:
        column (str): Column name.
        values_list (list): The list of banned values.
    """
    return df[~df[column].isin(values_list)]