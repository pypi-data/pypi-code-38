"""
Copyright (C) Enzo Busseti 2019.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
#import pandas as pd
import numba as nb
import logging
logger = logging.getLogger(__name__)

__all__ = ['HarmonicBaseline']  # , 'baseline_autotune', 'AutotunedBaseline']


@nb.jit(nopython=True)
def featurize_index_for_baseline(seconds, periods, trend=False):
    X = np.zeros((len(seconds), 1 + 2 * len(periods) + trend))
    for i, period in enumerate(periods):  # in seconds
        X[:, 2 * i] = np.sin(2 * np.pi * seconds / period)
        X[:, 2 * i + 1] = np.cos(2 * np.pi * seconds / period)
    X[:, -1 - trend] = np.ones(len(seconds))
    if trend:
        X[:, -1] = seconds / 1E9  # roughly around 1
    return X


@nb.jit(nopython=True)
def fit_seasonal_baseline(X, y):
    return np.linalg.solve(X.T @ X + 1E-5 * np.eye(X.shape[1]),
                           X.T @ y)


@nb.jit(nopython=True)
def predict_with_baseline(X, parameters):
    return X @ parameters


def index_to_seconds(index):
    return np.array(index.astype(np.int64) / 1E9)


@nb.jit(nopython=True)
def make_periods(daily_harmonics,
                 weekly_harmonics,
                 annual_harmonics):
    # print(daily_harmonics, weekly_harmonics, annual_harmonics)
    PERIODS = np.empty(daily_harmonics + weekly_harmonics + annual_harmonics)
    base_periods = (24 * 3600.,  # daily
                    24 * 7 * 3600,  # weekly
                    8766 * 3600)  # annual
    i = 0
    for j in range(daily_harmonics):
        PERIODS[i] = base_periods[0] / (j + 1)
        i += 1
    for j in range(weekly_harmonics):
        PERIODS[i] = base_periods[1] / (j + 1)
        i += 1
    for j in range(annual_harmonics):
        PERIODS[i] = base_periods[2] / (j + 1)
        i += 1
    assert i == len(PERIODS)

    # if daily:
    #     PERIODS[i * harmonics : (i + 1) * harmonics] = \
    #         base_periods[0] / np.arange(1, harmonics + 1)
    #     i += 1
    # if weekly:
    #     PERIODS[i * harmonics : (i + 1) * harmonics] = \
    #         base_periods[1] / np.arange(1, harmonics + 1)
    #     i += 1
    # if annual:
    #     PERIODS[i * harmonics : (i + 1) * harmonics] = \
    #         base_periods[2] / np.arange(1, harmonics + 1)
    #     i += 1

    return PERIODS


class HarmonicBaseline:

    def __init__(self,
                 train,
                 daily_harmonics=4,
                 weekly_harmonics=0,
                 annual_harmonics=4,
                 trend=False):
        # if not isinstance(data, pd.Series):
        #     raise ValueError(
        #         'Train data must be a pandas Series')
        self.daily_harmonics = daily_harmonics
        self.weekly_harmonics = weekly_harmonics
        self.annual_harmonics = annual_harmonics
        # self.harmonics = harmonics
        self.trend = trend
        self.periods = make_periods(self.daily_harmonics,
                                    self.weekly_harmonics,
                                    self.annual_harmonics)
        # print(self.periods)
        # self.name = data.name
        self._train_baseline(train)
        self._baseline = self._predict_baseline(train.index)

    def _train_baseline(self, train):

        Xtr = featurize_index_for_baseline(index_to_seconds(train.index),
                                           self.periods,
                                           trend=self.trend)
        ytr = train.values
        baseline_params = fit_seasonal_baseline(Xtr, ytr)
        # print('fitted parameters: ', baseline_params)
        self.baseline_params = baseline_params

    def _predict_baseline(self, index):
        Xte = featurize_index_for_baseline(index_to_seconds(index),
                                           self.periods,
                                           trend=self.trend)
        return predict_with_baseline(Xte, self.baseline_params)
