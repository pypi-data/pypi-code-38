from abc import ABC, abstractmethod
import pandas as pd


class Feature(ABC):

    def __init__(self, df, column):
        assert isinstance(df, pd.DataFrame), "Pass a DataFrame"
        assert column in df, "The column is not present in the DataFrame, pass a valid column name"
        
        self.df = df
        self.column = column

    @abstractmethod
    def stack(self): pass
