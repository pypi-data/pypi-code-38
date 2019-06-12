from typing import Dict, List, Set
from .coltag import ColTag
from pandas import DataFrame
from collections import defaultdict

# TaggedDataFrame knows all the column names of a DataFrame and which
# tags each has been given. It can return a list of column names
# based on given tags.
class TaggedDataFrame():
    def __init__(self, df: DataFrame):
        self.tags: Dict[str, List[ColTag]] = defaultdict(lambda: [])
        self.frame = df
        for name in df.columns.values:
            self.tags[name] = [ColTag.original]

    def tagged_as(self, tag: ColTag) -> List[str]:
        col_names: List[str] = []

        for name, tags in self.tags.items():
            if tag in tags:
                col_names.append(name)

        return col_names
    
    def remove(self, cols: List[str]) -> None:
        for name in cols:
            del self.tags[name]
        
    def retrive(self, with_tags: List[ColTag] = [], without: List[ColTag] = []) -> List[str]:
        cols_wanted: Set[str] = set()

        if len(with_tags) == 0:
            cols_wanted = set(self.tags.keys())
        else:
            for tag in with_tags:
                cols_wanted = cols_wanted.union(set(self.tagged_as(tag))) 
        
        for tag in without:
            cols_wanted = cols_wanted.difference(set(self.tagged_as(tag)))

        return list(cols_wanted)
    
    def tag_column(self, name: str, tag: ColTag) -> None:
        self.tags[name].append(tag)
    
    def tag_column_multi(self, name: str, tags: List[ColTag]) -> None:
        for tag in tags:
            self.tag_column(name, tag)