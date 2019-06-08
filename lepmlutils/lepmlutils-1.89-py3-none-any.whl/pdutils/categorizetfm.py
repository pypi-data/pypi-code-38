from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import List

# CategorizeTfm casts all string/object columns to category
# columns and for each of these creates an integer mapping 
# column. 
class CategorizeTfm(Transform):
    def __init__(self):
        self.altered: List[str] = []
    
    def operate(self, df: TaggedDataFrame) -> None:
            for col_name in df.frame.select_dtypes(include="object").columns.values:
                mapping_col_name = col_name + "_mapping" 
                assert(mapping_col_name not in df.frame)
                df.frame[col_name] = df.frame[col_name].astype('category')
                df.frame[mapping_col_name] = df.frame[col_name].cat.codes

                df.tag_column(col_name, ColTag.modified)
                df.tag_column(col_name, ColTag.categorized)
                df.tag_column(mapping_col_name, ColTag.mapping)

    def re_operate(self, new_df: TaggedDataFrame) -> None:
        self.operate(new_df)

