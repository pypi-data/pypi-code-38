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

from .autoregressive import AutoRegressive
from .baseline import HarmonicBaseline

logger = logging.getLogger(__name__)

__all__ = ['Autotune_AutoRegressive', 'AutotunedBaseline']


def Autotune_AutoRegressive(train_residuals,
                            test_residuals,
                            future_lag,
                            P=None,
                            past_lag=None):

    P_range = range(0, train_residuals.shape[1] - 1) if P is None else [P]
    past_lag_range = range(1, future_lag *
                           2) if past_lag is None else [past_lag]

    ar_model = AutoRegressive(train_residuals,
                              test_residuals,
                              past_lag=1 if past_lag is None else past_lag,
                              future_lag=future_lag,
                              P=0 if P is None else P)

    # Ps = np.arange(0, P_range)
    # past_lags = np.arange(1, past_lag_range)
    result_RMSE = pd.DataFrame(index=past_lag_range,
                               columns=P_range)
    for test_past_lag in past_lag_range:
        ar_model.past_lag = test_past_lag
        for test_P in P_range:
            ar_model.P = test_P
            # if not np.isnan(result.loc[past_lag, P]):
            #     continue
            ar_model.fit_AR()

            print()
            print()
            print('past_lag = %d, P = %d' % (
                ar_model.past_lag, ar_model.P))
            print('test RMSE:', ar_model.test_RMSE)
            print()
            print()

            result_RMSE.loc[test_past_lag, test_P] = ar_model.test_RMSE
            if (P is not None) or ((test_P > 0) and result_RMSE.loc[
                    test_past_lag, test_P] > result_RMSE.loc[test_past_lag, test_P - 1]):
                break
        if (past_lag is not None) or (test_past_lag > 1 and result_RMSE.min(
                1)[test_past_lag] > result_RMSE.min(1)[test_past_lag - 1]):
            break
    print('converged!')
    best_P = result_RMSE.min().idxmin()
    best_past_lag = result_RMSE.min(1).idxmin()
    return AutoRegressive(train_residuals,
                          test_residuals,
                          past_lag=best_past_lag,
                          future_lag=future_lag,
                          P=best_P)


def baseline_autotune(train, test, min_harmonics=3,
                      trend=None,
                      daily_harmonics=None,
                      weekly_harmonics=None,
                      annual_harmonics=None):

    results_test_RMSE = {}

    train = train.dropna()
    test = test.dropna()

    BOUND_WEEKLY = 6

    max_daily = min_harmonics
    max_weekly = min_harmonics
    max_annual = min_harmonics

    while True:

        daily_harmonics_range = range(max_daily) if \
            daily_harmonics is None else [daily_harmonics]
        weekly_harmonics_range = range(max_weekly) if \
            weekly_harmonics is None else [weekly_harmonics]
        annual_harmonics_range = range(max_annual) if \
            annual_harmonics is None else [annual_harmonics]
        trend_range = [False, True] if \
            trend is None else [trend]

        for daily_harmonics_test in daily_harmonics_range:
            for weekly_harmonics_test in weekly_harmonics_range:
                for annual_harmonics_test in annual_harmonics_range:
                    for trend_test in trend_range:
                        if (daily_harmonics_test, weekly_harmonics_test,
                                annual_harmonics_test, trend_test) \
                                in results_test_RMSE:
                            continue
                        baseline = HarmonicBaseline(train,
                                                    daily_harmonics_test,
                                                    weekly_harmonics_test,
                                                    annual_harmonics_test,
                                                    trend_test)

                        test_RMSE = np.sqrt(((test - baseline._predict_baseline(
                            test.index))**2).mean())
                        # print('test_RMSE:, ', test_RMSE)
                        results_test_RMSE[(daily_harmonics_test,
                                           weekly_harmonics_test,
                                           annual_harmonics_test,
                                           trend_test)] = test_RMSE

        current_best = min(results_test_RMSE, key=results_test_RMSE.get)

        current_best_daily = current_best[0]
        current_best_weekly = current_best[1]
        current_best_annual = current_best[2]

        if ((current_best_daily < max_daily - 1) or
            daily_harmonics is not None) and \
           ((current_best_weekly < max_weekly - 1) or
            weekly_harmonics is not None) and \
           ((current_best_annual < max_annual - 1) or
                annual_harmonics is not None):
            print('tried %d baseline parameter combinations' %
                  len(results_test_RMSE))
            print('optimal baseline parameters: ', current_best)
            print('test RMSE: ', results_test_RMSE[current_best])
            print('test std. dev.: ', test.std())
            print()
            return current_best

        max_daily = max(max_daily, current_best_daily + 2)
        max_weekly = max(max_weekly, current_best_weekly + 2)
        max_annual = max(max_daily, current_best_annual + 2)


def AutotunedBaseline(train, test, **kwargs):
    print('autotuning baseline for column %s' % train.name)
    params = baseline_autotune(train, test, **kwargs)
    return HarmonicBaseline(train.dropna(), *params)
