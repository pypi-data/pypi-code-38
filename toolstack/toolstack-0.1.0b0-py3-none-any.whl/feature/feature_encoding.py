import pandas as pd
import numpy as np
from .feature_base import Feature


class LabelEncoder(Feature):
    """
    Label encodes the data passed

    Parameters
    ----------
    df : DataFrame
        The df to perform case operation on.
    column : string, int
        The column selected should be present in the Dataframe passed

    Returns
    -------
    DataFrame
    """

    def __init__(self, df, column):
        super(LabelEncoder, self).__init__(df, column)
        self.df = df.copy()
        self.__mapper = {}

    def stack(self):
        unique_values = self.df[self.column].unique()
        for idx, val in enumerate(unique_values):
            if val not in self.__mapper.keys():
                self.__mapper[val] = idx
        
        self.df[self.column] = self.df[self.column].map(self.__mapper)
        self.inverse = {y: x for x, y in self.__mapper.items()}

        return (self.df)


class CountEncoder(Feature):
    """
    Count encodes the data passed

    Parameters
    ----------
    df : DataFrame
        The df to perform case operation on.
    column : string, int
        The column selected should be present in the Dataframe passed

    Returns
    -------
    DataFrame
    """

    def __init__(self, df, column, transformation = None):
        super(CountEncoder, self).__init__(df, column)
        self.transformation = transformation
        self.df = df.copy()

    def stack(self):
        if self.transformation == 'log':
            self.__mapper = self.df[self.column].value_counts().to_dict()
            self.__mapper = {x: np.log(y) for x, y in self.__mapper.items()}
        else:
            self.__mapper = self.df[self.column].value_counts().to_dict()

        self.df[self.column] = self.df[self.column].map(self.__mapper)
        self.inverse = {y: x for x,y in self.__mapper.items()}

        return (self.df)
        

class TargetEncoder(Feature):
    """
    Encode the target into the data passed

    Parameters
    ----------
    df : DataFrame
        The df to perform case operation on.
    column : string, int
        The column selected should be present in the Dataframe passed
    strategy : string
        Choose between ['count', 'conditional', 'percentage']

    Returns
    -------
    DataFrame
    """

    def __init__(self, df, column, target, strategy=None):
        super(TargetEncoder, self).__init__(df, column)
        self.strategy = strategy
        self.target = target
        self.df = df.copy()

    def stack(self): 
        
        if not self.strategy or self.strategy == 'count':
            self.__mapper = self.df[self.target].value_counts().to_dict()
            self.df[self.column] = self.df[self.target].map(self.__mapper)

        elif self.strategy == 'conditional':
            unique_values = self.df[self.column].unique().tolist()
            unique_classes = self.df[self.target].unique().tolist()

            for val in unique_values:
                for c in unique_classes:
                    self.df.loc[(self.df[self.target] == c) & (self.df[self.column] == val), self.column] =\
                         len(self.df[(self.df[self.column] == val) & (self.df[self.target] == c)]) /\
                         len(self.df[self.df[self.column] == val])

        elif self.strategy == 'percentage':
            unique_values = self.df[self.column].unique().tolist()
            unique_classes = self.df[self.target].unique().tolist()

            for val in unique_values:
                for c in unique_classes:
                    self.df.loc[(self.df[self.target] == c) & (self.df[self.column] == val) , self.column] =\
                         len(self.df[(self.df[self.column] == val) & (self.df[self.target] == c)]) /\
                         len(self.df)

        return self.df
