from .transform import Transform
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from typing import List
from scipy import stats
from .help import *
import pandas as pd
import pickle

# ClassifierReplaceTfm replaces all bad values in the given columns with
# the outputs of a classifier.
class ClassifierReplaceTfm(Transform):
    def __init__(self, cols: List[str], classifier):
        self.cols = cols
        self.cls = classifier
        self.zoo = {}

    def operate(self, df: TaggedDataFrame) -> None:
        for name in self.cols:
            features = all_cols_except(df, [name])
            self.cls.fit(df.frame[features], df.frame[name])
            self.zoo[name] = pickle.dumps(self.cls)



        

