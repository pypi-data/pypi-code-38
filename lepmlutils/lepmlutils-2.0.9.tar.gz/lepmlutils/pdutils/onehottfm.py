from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from .help import all_cols_except
from typing import List, Set
import pandas as pd

# OnehotTfm replaces all categorical columns in the
# dataframe with one-hot encoded columns.
class OnehotTfm(Transform):
    def __init__(self, to_convert: List[str]):
        self.to_convert = to_convert
    
    def operate(self, df: TaggedDataFrame) -> None:
        onehot = pd.get_dummies(df.frame[self.to_convert])
        new_cols = all_cols_except(onehot, df.frame.columns.values)
        self.added_cols = new_cols
        self.confirm_all_dropped(onehot) 

        self.drop_columns(df)

        for name in new_cols:
            df.frame[name] = onehot[name]
            df.tag_column_multi(name, [ColTag.engineered, ColTag.onehot])
        
    def confirm_all_dropped(self, df: pd.DataFrame):
        dropped = set(self.to_convert) - set(df.columns.values)
        if len(dropped) < len(self.to_convert):
            raise ValueError("the following columns were not one-hot encoded: ", *set(self.to_convert) - dropped)

    def drop_columns(self, df: TaggedDataFrame):
        df.frame.drop(self.to_convert, axis=1, inplace=True)
        df.remove(self.to_convert)

    # re_operate relies on pd.get_dummies, but any columns 
    # that were added initially but aren't this time are
    # added as columns of 0's, and no columns not added on
    # the first operation are added.
    def re_operate(self, new_df: TaggedDataFrame) -> None:
        onehot = pd.get_dummies(new_df.frame[self.to_convert])
        self.confirm_all_dropped(onehot)
        self.drop_columns(new_df)
        
        for name in self.added_cols:
            if name in onehot:
                new_df.frame[name] = onehot[name]
            else:
                new_df.frame[name] = 0
            
            new_df.tag_column_multi(name, [ColTag.engineered, ColTag.onehot])

