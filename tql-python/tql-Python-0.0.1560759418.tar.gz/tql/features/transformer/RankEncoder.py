#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = 'rank_encoder'
__author__ = 'JieYuan'
__mtime__ = '19-3-11'
"""
from collections import OrderedDict

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class RankEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, topn=None):
        self.topn = topn

    def fit(self, series: pd.Series):
        _ = series.value_counts(True)[:(self.topn if self.topn else 10000)]
        print("Coverage: %.2f %%" % (_.sum() * 100))
        self.ranker = (_.rank(method='first') - 1).to_dict(OrderedDict)
        print(self.ranker)
        return self

    def transform(self, series: pd.Series):
        return series.map(self.ranker)


if __name__ == '__main__':
    s = pd.Series(['a', 'a', 'b', 'b', 'c'])

    re = RankEncoder()

    print(re.fit_transform(s))
