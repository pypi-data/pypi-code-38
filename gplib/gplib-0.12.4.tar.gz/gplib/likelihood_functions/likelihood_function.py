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


class LikelihoodFunction(object):
    """

    """
    def __init__(self):

        self.gp = None

    def __copy__(self):

        copyed_object = self.__class__()

        return copyed_object

    def set_gp(self, gp):
        """

        :param gp:
        :type gp:
        :return:
        :rtype:
        """
        self.gp = gp

    def get_log_likelihood(self, data, grad_needed=False):
        """

        :param data:
        :param grad_needed:
        :return:
        """
        marginal = self.gp.inference_method.marginalize_gp(data['X'], data['Y'])

        log_likelihood = self.log_likelihood(data, marginal)

        result = (log_likelihood, )

        if grad_needed:
            dlog_likelihood_dtheta = self.dlog_likelihood_dtheta(data, marginal)
            result += (dlog_likelihood_dtheta, )

        if len(result) == 1:
            result = result[0]

        return result

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

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dlog_likelihood_dtheta(self, marginal, data):
        """
        Measure the gradient log Likelihood

        :param marginal:
        :type marginal:
        :param data:
        :type data:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_log_predictive_density(self, data):
        """
        Measure the log predictive density

        :param data:
        :type data:
        :return:
        :rtype:
        """
        mean = self.gp.mean_function.marginalize_mean(data['X'])
        var = self.gp.covariance_function.marginalize_covariance(
            data['X'],
            only_diagonal=True
        )
        return self.log_density(data['Y'], var, mean)

    def get_log_loocv_density(self, data):
        """
        Measure the log predictive density

        :param data:
        :type data:
        :return:
        :rtype:
        """

        mean, var = self.gp.inference_method.loocv(data['X'], data['Y'])
        return self.log_density(data['Y'], var, mean)

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

        raise NotImplementedError("Not Implemented. This is an interface.")
