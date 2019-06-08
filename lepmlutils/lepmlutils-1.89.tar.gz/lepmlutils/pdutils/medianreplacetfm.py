from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import List
import pandas as pd

# MedianReplaceTfm replaces all bad values in number
# columns with the median value of that column and all
# bad values in string/object columns with the value 
# "unknown".
class MedianReplaceTfm(Transform):
    def __init__(self):
        self.altered: List[str] = []
    
    def operate(self, df: TaggedDataFrame) -> None:
        df.frame.apply(self.median_replace, args=(df,))

    def median_replace(self, col: pd.Series, df: TaggedDataFrame) -> None:
        if col.isna().any():
            try:
                    df.frame[col.name] = col.fillna(col.median())
            except TypeError: 
                    assert "unknown" not in col.values
                    df.frame[col.name] = col.fillna("unknown")
        
            df.tag_column(col.name, ColTag.modified)
    
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.operate(new_df)

