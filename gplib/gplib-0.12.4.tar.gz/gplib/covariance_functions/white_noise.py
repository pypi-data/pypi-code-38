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

from .covariance_function import CovarianceFunction
from ..parameters.optimizable_parameter import OptimizableParameter
from ..parameters.log_parameter_transformation import LogParameterTransformation


class WhiteNoise(CovarianceFunction):
    """

    """
    def __init__(self, ov2=1e-8):

        hyperparams = [
            OptimizableParameter(
                'output_variance', LogParameterTransformation,
                default_value=ov2
            )
        ]

        super(WhiteNoise, self).__init__(hyperparams)

    def covariance(self, mat_a, mat_b=None, only_diagonal=False):
        """
        Measures the distance matrix between solutions of A and B, and
        applies the kernel function element-wise to the distance matrix.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """
        len_a = len(mat_a)
        if mat_b is not None:
            len_b = len(mat_b)

            return np.zeros((len_a, len_b))

        if only_diagonal:
            return np.square(self.get_param_value('output_variance')) * \
                np.ones((len_a, 1))

        return np.square(self.get_param_value('output_variance')) * \
            np.eye(len_a)

    def dk_dx(self, mat_a, mat_b=None):
        """
        Measures gradient of the distance between solutions of A and B in X.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :param mat_b: List of solutions in lines and dimensions in columns.
        :return: 3D array with the gradient in every dimension of X.
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dk_dtheta(self, mat_a, mat_b=None, trans=False):
        """
        Measures gradient of the distance between solutions of A and B in the
        hyper-parameter space.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param trans: Return results in the transformed space.
        :type trans:
        :return: 3D array with the gradient in every
         dimension the length-scale hyper-parameter space.
        :rtype:
        """

        len_a = len(mat_a)
        if mat_b is not None:
            len_b = len(mat_b)

            return np.zeros((len_a, len_b)),

        dk_dov = np.eye(len_a) * \
            2.0 * self.get_param_value('output_variance')

        if trans:
            dk_dov = self.get_hyperparam('output_variance').grad_trans(dk_dov)

        return dk_dov,
