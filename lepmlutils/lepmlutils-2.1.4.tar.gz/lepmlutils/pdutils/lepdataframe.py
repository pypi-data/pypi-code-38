from __future__ import annotations
from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from pandas import DataFrame
from typing import List

class LepDataFrame(TaggedDataFrame):
    def __init__(self, df: DataFrame):
        super().__init__(df)
        self.applied: List[Transform] = []
    
    def apply(self, tfm: Transform) -> None:
        tfm.operate(self)
        self.applied.append(tfm)
    
    def copy_from(self, df: 'LepDataFrame') -> None:
        for tfm in df.applied:
            self.reapply(tfm)
    
    def reapply(self, tfm: Transform) -> None:
        tfm.re_operate(self)
        self.applied.append(tfm)
    
    def apply_sequence(self, seq: List[Transform]) -> None:
        for tfm in seq:
            self.apply(tfm)