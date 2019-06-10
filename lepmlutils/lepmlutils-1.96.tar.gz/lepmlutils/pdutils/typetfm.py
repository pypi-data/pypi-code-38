from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from .help import all_cols_except
from typing import List
import pandas as pd

# TypeTfm transforms the type of the given columns to
# the given pandas type. 
class TypeTfm(Transform):
    def __init__(self, to_convert: List[str], data_type):
        self.to_convert = to_convert
        self.type = data_type
    
    def operate(self, df: TaggedDataFrame) -> None:
        for name in self.to_convert:
            df.frame[name] = df.frame[name].astype(self.type)
            df.tag_column(name, ColTag.modified)
        
    # Alias for operate.
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.operate(new_df)

