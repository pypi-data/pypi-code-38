from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import List
import pandas as pd

# FuncReplaceTfm takes a callback and replaces every bad
# value in the given columns with the output of that 
# callback. 
class FuncReplaceTfm(Transform):
    def __init__(self, callback, cols: List[str]):
        self.callback = callback
        self.cols = cols

    def operate(self, df: TaggedDataFrame) -> None:
        self.fill_bad_vals(df)

    def fill_bad_vals(self, df: TaggedDataFrame):
        for name in self.cols:
            df.frame[name] = df.frame[name].fillna(
                self.callback(
                    name,
                    df.frame
                )
            )
            df.tag_column(name, ColTag.modified)
    
    # re_operate fills the original columns with the 
    # values given by the callback, passing in the 
    # original data df.
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.fill_bad_vals(new_df)

