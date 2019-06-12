from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import Dict
import pandas as pd

# MedianReplaceTfm replaces all bad values in number
# columns with the median value of that column and all
# bad values in string/object columns with the value 
# "unknown".
class MedianReplaceTfm(Transform):
    def __init__(self):
        self.fill_vals: Dict = {}
    
    def operate(self, df: TaggedDataFrame) -> None:
        self.fill_bad_vals(df)

    def fill_bad_vals(self, df: pd.DataFrame):
        df.frame.apply(self.median_replace, args=(df,))

    def median_replace(self, col: pd.Series, df: TaggedDataFrame) -> None:
        if col.isna().any():
            try:
                    median = df.frame[col.name].median()
                    df.frame[col.name] = col.fillna(median)
                    self.fill_vals[col.name] = median
            except TypeError: 
                    assert "unknown" not in col.values
                    df.frame[col.name] = col.fillna("unknown")
                    self.fill_vals[col.name] = "unknown"
        
            df.tag_column(col.name, ColTag.modified)
    
    # re_operate fills the blanks in new columns with the
    # median values from the first operation. 
    # Any columns that still contain bad values have these
    # replaced with the median for those columns as usual.
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        for name, value in self.fill_vals.items():
            new_df.frame[name] = new_df.frame[name].fillna(value)

        self.fill_bad_vals(new_df)

