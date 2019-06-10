from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from .help import all_cols_except
from typing import List
import pandas as pd

# OnehotTfm replaces all categorical columns in the
# dataframe with one-hot encoded columns.
class OnehotTfm(Transform):
    def __init__(self, to_convert: List[str]):
        self.to_convert = to_convert
    
    def operate(self, df: TaggedDataFrame) -> None:
        onehot = pd.get_dummies(df.frame[self.to_convert])
        new_cols = all_cols_except(onehot, df.frame.columns.values)
        dropped = set(self.to_convert) - set(onehot.columns.values) 
        if len(dropped) < len(self.to_convert):
            raise ValueError("the following columns were not one-hot encoded: ", *set(self.to_convert) - dropped)
        df.frame.drop(self.to_convert, axis=1, inplace=True)
        df.remove(self.to_convert)

        for name in new_cols:
            df.frame[name] = onehot[name]
            df.tag_column_multi(name, [ColTag.engineered, ColTag.onehot])
        
    # Alias for operate.
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.operate(new_df)

