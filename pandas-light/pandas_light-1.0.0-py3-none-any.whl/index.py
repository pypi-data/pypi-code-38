import pandas as pd
import pandas_flavor as pf
from .tool import *

@pf.register_dataframe_method
def clear_index(df):
    return df.reset_index(drop=True)
