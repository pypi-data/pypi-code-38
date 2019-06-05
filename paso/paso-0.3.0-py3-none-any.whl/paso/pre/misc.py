import category_encoders as ce
import sklearn.decomposition as decomposition
from fancyimpute import SimpleFill
from sklearn.externals import joblib
from sklearn.feature_extraction import text
from sklearn.preprocessing import Normalizer, MinMaxScaler
import math

import pandas as pd
from pandas.util._validators import validate_bool_kwarg
import warnings

warnings.filterwarnings("ignore")

import numpy as np
from tqdm import tqdm

# paso imports
from paso.base import pasoModel,pasoError,_Check_No_NA_Values,get_paso_log,toDataFrame,is_DataFrame

__author__ = "Bruce_H_Cottman"
__license__ = "MIT License"
#
#

class TfIdfVectorizer(pasoModel):

    def __init__(self, **kwargs):
        super().__init__()
        self.vectorizer = text.TfidfVectorizer(**kwargs)

    def train(self, text):
        self.vectorizer.fit(text)
        return self

    def predict(self, text):
        return self.vectorizer.transform(text)

    def load(self, filepath):
        self.vectorizer = joblib.load(filepath)
        return self

    def save(self, filepath):
        joblib.dump(self.vectorizer, filepath)
        return self

class TruncatedSVD(pasoModel):

    def __init__(self, **kwargs):
        super().__init__()
        self.truncated_svd = decomposition.TruncatedSVD(**kwargs)

    def train(self, features):
        self.truncated_svd.fit(features)
        return self

    def predict(self, features):
        return self.truncated_svd.transform(features)

    def load(self, filepath):
        self.truncated_svd = joblib.load(filepath)
        return self

    def save(self, filepath):
        joblib.dump(self.truncated_svd, filepath)
        return self

class FillNan(pasoModel):
    def __init__(self, fill_method="zero", fill_missing=True, **kwargs):
        """
        Inputs NaN's using various filling methods like mean, zero, median, min, random


        Args:
            fill_method: How NaN's will be exchanged. Possible values: 'mean', 'zero', 'median', 'min', 'random'
            fill_missing: If True, transformer will fill NaN values by filling method
        """
        super().__init__()
        self.fill_missing = fill_missing
        self.filler = SimpleFill(fill_method)

    def transform(self, X):
        """
        Args:
            X: DataFrame with NaN's
        Returns:
            Dictionary with one key - 'X' corresponding to given DataFrame but without nan's

        """
        if self.fill_missing:
            X = self.filler.complete(X)
        return X

    def load(self, filepath):
        self.filler = joblib.load(filepath)
        return self

    def save(self, filepath):
        joblib.dump(self.filler, filepath)
        return self