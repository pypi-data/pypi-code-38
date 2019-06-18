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
import scipy.linalg

from .inference_method import InferenceMethod


class ExactGaussian(InferenceMethod):
    """

    """

    def marginalize_gp(self, data_x, data_y=None):
        """
        Get mean and covariance of following points

        :param data_x:
        :type data_x:
        :param data_y:
        :type data_y:
        :return:
        :rtype:
        """

        # Data assertions
        assert not np.isnan(data_x).any(), "NaN values in X"
        assert not np.isinf(data_x).any(), "Inf values in X"
        if data_y is not None:
            assert len(data_x) == len(data_y), "Data is not consistent"
            assert not np.isnan(data_y).any(), "NaN values in y"
            assert not np.isinf(data_y).any(), "Inf values in y"

        mean = self.gp.mean_function.marginalize_mean(data_x)
        covariance = self.gp.covariance_function.marginalize_covariance(data_x)
        l_matrix = InferenceMethod.safe_chol(covariance)

        marginal = {
            'mean': mean,
            'l_matrix': l_matrix
        }

        if data_y is not None:
            marginal['alpha'] = \
                scipy.linalg.cho_solve((l_matrix, True), data_y - mean)

        return marginal

    def loocv(self, data_x, data_y=None):
        """

        :param data_x:
        :type data_x:
        :param data_y:
        :type data_y:
        :return:
        :rtype:
        """
        covariance = self.gp.covariance_function.marginalize_covariance(data_x)
        l_matrix = InferenceMethod.safe_chol(covariance)

        inv_cov = scipy.linalg.cho_solve(
            (l_matrix, True),
            np.eye(l_matrix.shape[0])
        )

        diag_inv_cov = np.diagonal(inv_cov)[:, None]

        mean = data_y - np.divide(np.dot(inv_cov, data_y), diag_inv_cov)

        var = np.divide(1.0, diag_inv_cov)

        return mean, var
