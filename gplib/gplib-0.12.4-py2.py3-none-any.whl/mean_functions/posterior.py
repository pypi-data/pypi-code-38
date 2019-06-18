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

from .mean_function import MeanFunction


class Posterior(MeanFunction):
    """

    """
    def __init__(self, prior_gp, prior_data):

        self.prior_gp = prior_gp
        self.prior_data = prior_data

        super(Posterior, self).__init__(
            self.prior_gp.mean_function.get_hyperparams()
        )

    def mean(self, x):
        """
        Marginalize posterior mean

        :param x:
        :return:
        """
        marginal = self.prior_gp.inference_method.marginalize_gp(
            self.prior_data['X'],
            self.prior_data['Y']
        )

        ka_matrix = self.prior_gp.\
            covariance_function.marginalize_covariance(
                self.prior_data['X'], x)
        test_mean = self.prior_gp.mean_function.marginalize_mean(x)

        mean = np.dot(ka_matrix.T, marginal['alpha']) + test_mean

        return mean

    def dmu_dx(self, x):
        """

        :param x:
        :type x:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dmu_dtheta(self, x, trans=False):
        """

        :param x:
        :type x:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
