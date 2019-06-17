#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'CountEncoder'
__author__ = 'JieYuan'
__mtime__ = '19-1-10'
"""
import pandas as pd
from ...pipe import tqdm

from concurrent.futures import ProcessPoolExecutor
from sklearn.base import BaseEstimator, TransformerMixin


class CountEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, normalize=False, dropna=False):
        self.dropna = dropna
        self.normalize = normalize
        self.counter_ls = []

    def fit(self, df: pd.DataFrame):
        self.w = df.shape[1]
        self.counter_ls = list(self._pe(self._fit, tqdm(self._get_series_ls(df), 'Fitting ...'), self.w))
        return self

    def transform(self, df):
        assert self.w == df.shape[1]
        _ = self._pe(self._transform, tqdm(zip(self.counter_ls, self._get_series_ls(df)), 'Transforming ...'), self.w)
        return pd.concat(_, 1)

    # def fit_transform(self, df):
    #     return self.fit(df).transform(df)

    def _fit(self, s: pd.Series):
        _ = (s.value_counts(normalize=self.normalize, dropna=self.dropna)
             .reset_index(name='count_' + s.name))
        return _

    def _transform(self, args):
        c, s = args
        _ = (s.to_frame('index')
             .merge(c, 'left')
             .drop('index', 1)
             .fillna(0))  # 不在训练集的补0
        return _

    def _pe(self, func, iterable, feat_num):
        with ProcessPoolExecutor(5 if feat_num > 5 else feat_num) as pool:
            return pool.map(func, iterable)

    def _get_series_ls(self, df):
        return [v for k, v in df.items()]


if __name__ == '__main__':
    df = pd.DataFrame({'a': ['1', '2'], 'b': ['2', '2']})
    c = CountEncoder()
    c.fit(df)
    print(c)
    print(c.transform(df))
    print(c.fit_transform(df))
