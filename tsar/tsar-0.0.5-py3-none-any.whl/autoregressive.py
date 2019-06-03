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
import scipy.sparse.linalg as spl
logger = logging.getLogger(__name__)

__all__ = ['AutoRegressive']  # , 'Autotune_AutoRegressive']


def lagged_covariance(train_normalized, lag):
    N = train_normalized.shape[1]
    raw = pd.concat((train_normalized,
                     train_normalized.shift(lag)),
                    axis=1).cov().iloc[:N, N:]
    return raw


def iterative_denoised_svd(dataframe, P, T=10):
    y = pd.DataFrame(0., index=dataframe.index,
                     columns=dataframe.columns)
    for t in range(T):
        u, s, v = spl.svds(dataframe.fillna(y), P + 1)
        dn_u, dn_s, dn_v = u[:, 1:], s[1:] - s[0], v[1:]
        new_y = dn_u @ np.diag(dn_s) @ dn_v
        print('MSE(y_%d - y_{%d}) = %.2e' % (
            t + 1, t, ((new_y - y)**2).mean().mean()))
        y.iloc[:, :] = dn_u @ np.diag(dn_s) @ dn_v
    return dn_u, dn_s, dn_v


@nb.jit(nopython=True)
def schur_complement(array_with_na, Sigma):
    null_mask = np.isnan(array_with_na)
    y = array_with_na[~null_mask]

    # A = Sigma[null_mask].T[null_mask]
    B = Sigma[null_mask].T[~null_mask].T
    C = Sigma[~null_mask].T[~null_mask]

    expected_x = B @ np.linalg.solve(C, y)
    array_with_na[null_mask] = expected_x
    return array_with_na


#@nb.jit(nopython=True)
def schur_complement_matrix(matrix_with_na,
                            null_mask,
                            Sigma):
    # null_mask = np.isnan(array_with_na)
    Y = matrix_with_na[:, ~null_mask]

    # A = Sigma[null_mask].T[null_mask]
    B = Sigma[null_mask].T[~null_mask].T
    C = Sigma[~null_mask].T[~null_mask]
    inv_C = np.linalg.inv(C)

    expected_X = B @ inv_C @ Y.T
    matrix_with_na[:, null_mask] = expected_X.T
    return matrix_with_na


def guess_matrix(matrix_with_na, Sigma, min_rows=5):
    print('guessing matrix')
    full_null_mask = matrix_with_na.isnull()
    ranked_masks = pd.Series([tuple(el) for el in
                              full_null_mask.values]).value_counts().index

    for i in range(len(ranked_masks)):
        print('null mask %d' % i)
        mask_indexes = (full_null_mask ==
                        ranked_masks[i]).all(1)
        if mask_indexes.sum() <= min_rows:
            break
        print('there are %d rows' % mask_indexes.sum())
        matrix_with_na.loc[mask_indexes] = schur_complement_matrix(
            matrix_with_na.loc[mask_indexes].values,
            np.array(ranked_masks[i]),
            Sigma)
        # print(matrix_with_na)
    return matrix_with_na


class AutoRegressive:

    def __init__(self, train_normalized,
                 test_normalized,
                 future_lag,
                 past_lag, P):
        self.train_normalized = train_normalized
        self.test_normalized = test_normalized
        self.future_lag = future_lag
        self.past_lag = past_lag
        self.N = self.train_normalized.shape[1]
        self.P = P
        self.svd_results = {}
        self.embedding_covariances = {}
        self.full_covariances = {}
        # self.fit_AR_low_rank()
        self.fit_AR()

    def plot(self):
        self.train_sq_err = self.test_model(self.train_normalized)
        self.plot_RMSE(np.sqrt(self.train_sq_err.mean()), train=True)
        self.test_normalized.std().plot(color='r',
                                        style='--')
        self.plot_RMSE(np.sqrt(self.test_sq_err.mean()), train=False)

    @property
    def test_RMSE(self):
        return np.sqrt(self.test_sq_err.mean().mean())

    @property
    def lag(self):
        return self.future_lag + self.past_lag

    def fit_AR(self):
        self._fit_low_rank_covariances()
        self._fit_full_AR()
        self._assemble_Sigma()
        self.test_sq_err = self.test_model(self.test_normalized)

    def _fit_low_rank_covariances(self):
        if self.P not in self.svd_results:
            print('computing rank %d svd of train data' % self.P)
            self.svd_results[self.P] = \
                iterative_denoised_svd(self.train_normalized,
                                       P=self.P)
            self.embedding_covariances[self.P] = {}
        u, s, v = self.svd_results[self.P]
        embedding = pd.DataFrame(u,
                                 index=self.train_normalized.index)
        print('computing lagged covariances')
        # self.lagged_covariances = {}
        # self.lagged_covariances[0] = \
        #     lagged_covariance(
        #         self.train_normalized, 0)
        for i in range(0, self.lag):
            # self.lagged_covariances[i] = lagged_covariance_svd(
            #    self.train_normalized, i, self.P)
            if i not in self.embedding_covariances[self.P]:
                self.embedding_covariances[self.P][i] = \
                    v.T @ np.diag(s) @ \
                    lagged_covariance(embedding, i)\
                    @ np.diag(s) @ v

            # self.lagged_covariances[i] = \
            #     v.T @ np.diag(s) @ lagged_covariance(
            #     embedding, i) @ np.diag(s) @ v

    def _fit_full_AR(self):
        for i in range(self.lag):  # self.lag):
            # self.lagged_covariances[i] = lagged_covariance_svd(
            #    self.train_normalized, i, self.P)
            if i not in self.full_covariances:
                print('computing raw covariance lag %d' % i)
                self.full_covariances[i] = lagged_covariance(
                    self.train_normalized, i)

    def _assemble_Sigma(self):
        print('adding diagonal to covariance')
        # self.raw_covariances = {}
        for i in range(self.lag):  # self.lag):
            # self.lagged_covariances[i] = lagged_covariance_svd(
            #    self.train_normalized, i, self.P)
            # self.raw_covariances[i] = lagged_covariance(
            #     self.train_normalized, i)

            self.embedding_covariances[self.P][i] += \
                np.diag(np.diag(self.full_covariances[i]) -
                        np.diag(self.embedding_covariances[self.P][i]))
            assert np.allclose(
                np.diag(self.embedding_covariances[self.P][i]) -
                np.diag(self.full_covariances[i]), 0)

        print('assembling covariance matrix')
        self.Sigma = pd.np.block(
            [[self.embedding_covariances[self.P][i].values.T
              if i > 0 else
              self.embedding_covariances[self.P][-i].values
                for i in range(-j, self.lag - j)]
                for j in range(self.lag)])
        assert np.allclose((self.Sigma - self.Sigma.T), 0)

    def plot_RMSE(self, RMSE, train):
        N = self.train_normalized.shape[1]
        for i in range(self.future_lag):
            RMSE[self.N * i:self.N * (i + 1)].plot(color='b' if train
                                                   else 'r',
                                                   alpha=1. / (i + 1))

    def test_model(self, data):
        test_concatenated = pd.concat([
            data.shift(-i)
            for i in range(self.lag)], axis=1)

        null_mask = pd.Series(False,
                              index=test_concatenated.columns)
        null_mask[self.past_lag * self.N:] = True

        to_guess = pd.DataFrame(test_concatenated, copy=True)
        to_guess.loc[:, null_mask] = np.nan
        # pd.DataFrame(data=
        guessed = guess_matrix(to_guess, self.Sigma)
        # index=to_guess.index,
        # columns=to_guess.columns)

        squared_error = (test_concatenated.loc[:, null_mask]
                         - guessed.loc[:, null_mask])**2
        return squared_error

    def test_model_NEW(self, data):
        test_concatenated = pd.concat([
            data.shift(-i)
            for i in range(self.lag)], axis=1)

        null_mask = pd.Series(False,
                              index=test_concatenated.columns)
        null_mask[self.past_lag * self.N:] = True

        to_guess = pd.DataFrame(test_concatenated, copy=True)
        to_guess.loc[:, null_mask] = np.nan
        guessed = guess_matrix(to_guess, self.Sigma).iloc[
            :, self.past_lag * self.N:]
        assert guessed.shape[1] == self.N * self.future_lag
        guessed_at_lag = []
        for i in range(self.future_lag):
            to_append = guessed.iloc[:, self.N * i: self.N *
                                     (i + 1)].shift(i + self.past_lag)
            guessed_at_lag.append(to_append)
        return guessed_at_lag
