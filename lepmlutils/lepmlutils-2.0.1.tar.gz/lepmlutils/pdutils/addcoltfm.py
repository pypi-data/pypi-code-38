from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import List
import pandas as pd

# AddColTfm adds an extra column to the data frame whose
# value is the sum of several existing columns.
class AddColTfm(Transform):
    def __init__(self, name: str, existing_cols: List[str]):
        col_count = len(existing_cols)
        if col_count < 2:
            raise ValueError("expected at least 2 columns to aggregate, got %d" % col_count)

        self.name = name
        self.existing_cols = existing_cols
    
    def operate(self, df: TaggedDataFrame) -> None:
        value = 0
        for name in self.existing_cols:
            value += df.frame[name]
        
        df.frame[self.name] = value
        df.tag_column(self.name, ColTag.engineered)
        
    # Alias for operate.
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.operate(new_df)

