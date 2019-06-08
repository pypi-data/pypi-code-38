#!python
from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
import pandas as pd

class PandasPick(object):
    def __init__(self, col_pick, flatten_single= True):
        self.col_pick= col_pick
        self.flatten_single= flatten_single

    def fit(self, data, input_split= False):
        return self

    def fit_transform(self, df):
        return self.transform(df)

    def transform(self, df):
        if self.flatten_single and len(self.col_pick)==1:  return df[self.col_pick[0]]
        else: return(df[self.col_pick])
