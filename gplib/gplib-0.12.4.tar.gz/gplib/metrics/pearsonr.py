# -*- coding: utf-8 -*-
#
#    Copyright 2019 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import scipy.stats.stats

from .metric import Metric


class Pearsonr(Metric):
    """

    """

    @staticmethod
    def measure(model, train_set, test_set=None, grad_needed=False):
        """

        :param model:
        :type model:
        :param train_set:
        :type train_set:
        :param test_set:
        :type test_set:
        :param grad_needed:
        :type grad_needed:
        :return:
        :rtype:
        """

        if test_set is None:
            raise TypeError("Test set should be provided")

        if grad_needed:
            raise NotImplementedError("Accuracy gradient")

        if test_set is None:
            raise TypeError("Test set should be provided")

        if grad_needed:
            raise NotImplementedError("RMSE gradient")

        posterior_gp = model.get_posterior(train_set)

        prediction = posterior_gp.mean_function.marginalize_mean(test_set['X'])

        assert np.all(np.isfinite(prediction)), "Non finite values"

        pearson_r = scipy.stats.stats.pearsonr(
            test_set['Y'].flatten(),
            prediction.flatten()
        )

        return -pearson_r[0]
