import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def hasnans(df):
    """Whether the DataFrame has any NA.
    """
    return df.isna().any().any()
