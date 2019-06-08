from __future__ import annotations
import pandas as pd
from pandas import DataFrame
from typing import List, Dict
import numpy as np

class Partition():
    def __init__(self, dataset: DataFrame, folds: int):
        self.folds = np.array_split(dataset, folds)
        self.test_index = 0
    

    def __iter__(self) -> "Partition":
        return self

    def __next__(self) -> Dict:
        if (self.exhausted()):
            raise StopIteration 

        folds = {
            "test": self.folds[self.test_index],
            "train": pd.concat(
                [*self.folds[:self.test_index], 
                *self.folds[self.test_index + 1:]]
            )
        }

        self.test_index += 1

        return folds

    def exhausted(self) -> bool:
        return self.test_index >= len(self.folds)
    
