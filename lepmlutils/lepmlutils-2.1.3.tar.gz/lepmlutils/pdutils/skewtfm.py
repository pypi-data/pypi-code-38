from .repeatabletfm import RepeatableTfm
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import List
from scipy import stats
import pandas as pd
import numpy as np

# SkewTfm skews all the given columns using box cox.
class SkewTfm(RepeatableTfm):
    def __init__(self, cols: List[str], max_skewness:float=0.75):
        self.cols = cols
        self.max_skewness = max_skewness

    def operate(self, df: TaggedDataFrame) -> None:
        for name in self.cols:
            if abs(stats.skew(df.frame[name].dropna())) > self.max_skewness:
                df.frame[name] = np.log1p(df.frame[name])
                df.tag_column(name, ColTag.modified)

