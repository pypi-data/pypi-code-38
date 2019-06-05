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
import pandas as pd
import numba as nb
import logging
import scipy.stats

from .baseline import HarmonicBaseline
from .autotune import AutotunedBaseline, Autotune_AutoRegressive
from .autoregressive import AutoRegressive  # , Autotune_AutoRegressive


logger = logging.getLogger(__name__)

__all__ = ['Model']


def compute_gaussian_interpolation(column, N=10, corrector=1E-5):
    xs = np.array([scipy.stats.norm.ppf(i) for i in np.concatenate(
        [[1. / len(column)], (np.arange(1, N) / N), [1 - 1. / len(column)]])])
    quantiles = np.array([column.quantile(i) for i in (np.arange(N + 1) / N)])

    if not np.all(np.diff(quantiles) > 0):

        new_quantiles = (quantiles * (1 - corrector) + quantiles[0] * corrector +
                         np.arange(len(quantiles)) * corrector * (quantiles[-1] - quantiles[0])
                         / (len(quantiles) - 1))

        assert np.all(np.diff(new_quantiles) > 0)
        assert np.isclose((new_quantiles - quantiles)[0], 0)
        assert np.isclose((new_quantiles - quantiles)[-1], 0)
        return xs, new_quantiles

    return xs, quantiles


def gaussianize(column, xs, quantiles):
    return np.interp(column, quantiles, xs)


def invert_gaussianize(column, xs, quantiles):
    return np.interp(column, xs, quantiles)


class Model:

    def __init__(
            self,
            data,
            future_lag,
            baseline_per_column_options={},
            P=None,
            past_lag=None):

        if not isinstance(data, pd.DataFrame):
            raise ValueError(
                'Train data must be a pandas DataFrame')
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError(
                'Train data must be indexed by a pandas DatetimeIndex.')
        if data.index.freq is None:
            raise ValueError('Train data index must have a frequency. ' +
                             'Try using the pandas.DataFrame.asfreq method.')
        self.frequency = data.index.freq
        self._columns = data.columns
        self.future_lag = future_lag
        self.data = data

        self.train = data.iloc[:-len(data) // 3]
        self.test = data.iloc[-len(data) // 3:]
        # prilen(train), len(test)

        self.baseline_per_column_options =\
            baseline_per_column_options
        self.P = P
        self.past_lag = past_lag

        self._fit_ranges()
        self._fit_gaussianization(self.train)

        self.gaussianized_train = self._gaussianize(self.train)
        self.gaussianized_test = self._gaussianize(self.test)

        self._fit_baselines(self.gaussianized_train,
                            self.gaussianized_test)

        self._residuals_stds = self._train_residuals.std()
        self._train_normalized_residuals = self._train_residuals / self._residuals_stds
        self._test_normalized_residuals = self._test_residuals / self._residuals_stds
        self._fit_AR()

        # TODO refit with full data

    def _fit_gaussianization(self, train):
        self.gaussanization_params = {}
        for col in self._columns:
            self.gaussanization_params[col] = \
                compute_gaussian_interpolation(train[col])

    def _gaussianize(self, data):
        return pd.DataFrame(
            {
                k: gaussianize(
                    data[k],
                    *
                    self.gaussanization_params[k]) for k in self._columns},
            index=data.index)[
                self._columns]

    def _invert_gaussianize(self, data):
        return pd.DataFrame(
            {
                k: invert_gaussianize(
                    data[k],
                    *self.gaussanization_params[k]) for k in self._columns},
            index=data.index)[
                self._columns]

    def _fit_ranges(self):
        self._min = self.train.min()
        self._max = self.train.max()

    def _clip_prediction(self, prediction):
        return prediction.clip(self._min, self._max, axis=1)

    # @property
    # def _train_baseline(self):
    #     return pd.concat(
    #         [pd.Series(self._baselines[col]._baseline,
    #             index=for col in self._columns], axis=1)

    # @property
    # def _test_baseline(self):
    #     return pd.concat(
    #         [self._baselines[col]._predict_baseline(self.test.index)
    #          for col in self._columns], axis=1)

    @property
    def _train_residuals(self):
        return self.gaussianized_train - self.predict_baseline(self.data.index)

    @property
    def _test_residuals(self):
        return self.gaussianized_test - self.predict_baseline(self.test.index)

    def predict(self, last_data, number_scenarios=0):
        print('last_data', last_data.shape)
        # print(last_data.index)
        if len(last_data) > self.lag:
            raise ValueError('Only provide the last data.')
        if not last_data.index.freq == self.frequency:
            raise ValueError('Provided data has wrong frequency.')
        len_chunk = len(last_data)
        for i in range(1, 1 + self.lag - len(last_data)):
            # print('i = ', i)
            t = last_data.index[len_chunk - 1] + i * self.frequency
            # print('adding row', t)
            last_data.loc[t] = np.nan
        print('last_data', last_data.shape)
        baseline = self.predict_baseline(last_data.index)
        print('baseline', baseline.shape)
        residuals = self._gaussianize(last_data) - baseline
        normalized_residuals = residuals / self._residuals_stds
        normalized_residuals_list = self._predict_normalized_residual_AR(
            normalized_residuals, number_scenarios)
        all_results = []
        for normalized_residuals in normalized_residuals_list:
            residuals = normalized_residuals * self._residuals_stds
            all_results.append(
                self._clip_prediction(self._invert_gaussianize(
                    residuals + baseline)))
            if not number_scenarios:
                return all_results[-1]
        return all_results

    def predict_baseline(self, index):
        return pd.concat(
            [pd.Series(
                self._baselines[col]._predict_baseline(index),
                index=index, name=col)
             for col in self._columns], axis=1)

    def _fit_baselines(self, train, test):
        self._baselines = {}
        for column in self._columns:
            if column in self.baseline_per_column_options:
                self._baselines[column] = AutotunedBaseline(
                    train[column],
                    test[column],
                    **self.baseline_per_column_options[column]
                )
            else:
                self._baselines[column] = AutotunedBaseline(
                    train[column],
                    test[column]
                )

    @property
    def Sigma(self):
        return self.ar_model.Sigma

    @property
    def lag(self):
        return self.ar_model.lag

    def _fit_AR(self):
        self.ar_model = Autotune_AutoRegressive(
            self._train_normalized_residuals,
            self._test_normalized_residuals,
            self.future_lag,
            self.P,
            self.past_lag)
        # print('computing lagged covariances')
        # self.lagged_covariances = {}
        # for i in range(self.lag):
        #     self.lagged_covariances[i] = \
        #         pd.concat((self._normalized_residuals,
        #                    self._normalized_residuals.shift(i)),
        #                   axis=1).corr().iloc[:len(self._columns),
        #                                       len(self._columns):]
        # print('assembling covariance matrix')
        # self.Sigma = pd.np.block(
        #     [[self.lagged_covariances[np.abs(i)].values
        #         for i in range(-j, self.lag - j)]
        #         for j in range(self.lag)]
        # )

    def _predict_concatenated_AR(self,
                                 concatenated,
                                 number_scenarios=0):

        # https://en.wikipedia.org/wiki/Schur_complement
        # (Applications_to_probability_theory_and_statistics)

        null_mask = concatenated.isnull().values
        y = concatenated[~null_mask].values

        A = self.Sigma[null_mask].T[null_mask]
        B = self.Sigma[null_mask].T[~null_mask].T
        C = self.Sigma[~null_mask].T[~null_mask]

        expected_x = B @ np.linalg.solve(C, y)
        concatenated[null_mask] = expected_x

        if number_scenarios:
            print('computing conditional covariance')
            Sigma_x = A - B @ np.linalg.inv(C) @ B.T
            samples = np.random.multivariate_normal(
                expected_x, Sigma_x, number_scenarios)
            sample_concatenations = []
            for sample in samples:
                concatenated[null_mask] = sample
                sample_concatenations.append(
                    pd.Series(concatenated, copy=True))
            return sample_concatenations

        return [concatenated]

    def plot_test_RMSEs(self):
        import matplotlib.pyplot as plt

        guessed_test_residuals_at_lag = self.ar_model.test_model_NEW(
            self.ar_model.test_normalized)
        all_results = []
        baseline = self.predict_baseline(self.test.index)

        for el in guessed_test_residuals_at_lag:
            residuals = el * self._residuals_stds
            all_results.append(
                self._clip_prediction(
                    self._invert_gaussianize(residuals + baseline)))
        inverted_baseline = self._invert_gaussianize(baseline)
        for column in self._columns:
            plt.figure()
            plt.plot([pd.np.sqrt((all_results[i][column] - self.test[column])**2).mean()
                      for i in range(self.future_lag)], 'k.-', label='AR prediction')
            plt.plot([pd.np.sqrt((inverted_baseline[column] - self.test[column])**2).mean()
                      for i in range(24)], 'k--', label='baseline')
            plt.title(column)
            plt.legend()
            plt.xlabel('prediction lag')
            plt.ylabel('RMSE')

    def _predict_normalized_residual_AR(self, chunk,
                                        number_scenarios=0):
        # chunk = model._normalized_residuals.iloc[-10:]
        assert len(chunk) == self.lag
        chunk_index = chunk.index

        concatenated = pd.concat(
            [
                chunk.iloc[i]
                for i in range(self.lag)
            ])

        filled_list = self._predict_concatenated_AR(concatenated,
                                                    number_scenarios)
        chunk_filled_list = []

        for filled in filled_list:
            chunk_filled = pd.concat(
                [filled.iloc[len(self._columns) * i:len(self._columns) * (i + 1)]
                    for i in range(self.lag)], axis=1).T
            chunk_filled.index = chunk_index
            chunk_filled_list.append(chunk_filled)

        return chunk_filled_list
