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

import scipy.linalg as spla

from .likelihood_function import LikelihoodFunction


class Gaussian(LikelihoodFunction):
    """

    """

    def log_likelihood(self, data, marginal):
        """
        Measure the log Likelihood

        :param data:
        :type data:
        :param marginal:
        :type marginal:
        :return:
        :rtype:
        """
        llikelihood = -np.sum(np.log(np.diag(marginal['l_matrix']))) - \
            0.5 * np.dot(
                    (data['Y'] - marginal['mean']).T,
                    marginal['alpha']
                )[0, 0] - \
            0.5 * marginal['l_matrix'].shape[0] * \
                np.log(2.0 * np.pi)

        return llikelihood

    def log_density(self, fy, var, mean):
        """
        Measure the log density

        :param fy:
        :type fy:
        :param var:
        :type var:
        :param mean:
        :type mean:
        :return:
        :rtype:
        """
        log_predictive_density = \
            -0.5 * np.log(var) - \
            np.power((fy - mean), 2) / (2.0 * var) - \
            0.5 * np.log(2 * np.pi)

        return log_predictive_density

    def dlog_likelihood_dtheta(self, data, marginal):
        """
        Measure the gradient log Likelihood

        :param data:
        :type data:
        :param marginal:
        :type marginal:
        :return:
        :rtype:
        """
        k_inv = spla.cho_solve(
            (marginal['l_matrix'], True),
            np.eye(marginal['l_matrix'].shape[0]))
        jacobian = np.outer(marginal['alpha'],
                            marginal['alpha']) - k_inv

        grad_llikelihood = []
        # Log amplitude gradient.
        _, dmu_dtheta = self.gp.mean_function.marginalize_mean(
            data['X'], dmu_dtheta_needed=True, trans=True)

        for dmu_dtheta_i in dmu_dtheta:
            grad_llikelihood.append(
                self._dlog_likelihood_dtheta(dmu_dtheta_i, jacobian))
        # Log amplitude gradient.
        _, dk_dtheta = self.gp.covariance_function.marginalize_covariance(
            data['X'], dk_dtheta_needed=True, trans=True)

        for dk_dtheta_i in dk_dtheta:
            grad_llikelihood.append(
                self._dlog_likelihood_dtheta(dk_dtheta_i, jacobian))

        return grad_llikelihood

    @staticmethod
    def _dlog_likelihood_dtheta(dk_dtheta, jacobian):
        """
        Measure the gradient of the log Likelihood

        :param jacobian:
        :return:
        """
        return 0.5 * np.trace(np.dot(jacobian, dk_dtheta))
