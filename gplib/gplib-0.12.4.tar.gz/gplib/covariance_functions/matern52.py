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

from .stationary_function import StationaryFunction
from ..parameters.optimizable_parameter import OptimizableParameter
from ..parameters.log_parameter_transformation import LogParameterTransformation

SQRT_5 = np.sqrt(5.0)


class Matern52(StationaryFunction):
    """

    """
    def __init__(self, ov2=1.0, ls=None, ard_dims=None):
        hyperparams = [
            OptimizableParameter(
                'output_variance', LogParameterTransformation,
                default_value=ov2
            )
        ]

        super(Matern52, self).__init__(hyperparams, ls, ard_dims)

    def stationary_function(self, sq_dist):
        """
        It applies the Matern (v=5/2) kernel function
        element-wise to the distance matrix.

        .. math::
            k_{M52}(r)=(1+\dfrac{\sqrt{5}r}{l} +
            \dfrac{5r^2}{3l^2}) exp (-\dfrac{\sqrt{5}r}{l})

        :param sq_dist: Distance matrix
        :type sq_dist:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """
        dist = np.sqrt(sq_dist)
        return np.multiply((1.0 + SQRT_5 * dist + (5.0 / 3.0) * sq_dist),
                           np.exp(-SQRT_5 * dist)) * \
            np.square(self.get_param_value('output_variance'))

    def dkr_dx(self, sq_dist, dr_dx):
        """
        Measures gradient of the kernel function in X.

        :param sq_dist: Square distance
        :type sq_dist:
        :param dr_dx:
        :type dr_dx:
        :return: 3D array with the gradient of the kernel function in every
         dimension of X.
        :rtype:
        """
        dist = np.sqrt(sq_dist)
        grad_r2 = -(5.0 / 6.0) * np.exp(-SQRT_5 * dist) * (1 + SQRT_5 * dist)
        return grad_r2[:, :, np.newaxis] * dr_dx * \
            np.square(self.get_param_value('output_variance'))

    def dkr_dtheta(self, sq_dist, trans):
        """
        Measures gradient of the kernel function in the
        hyper-parameter space.

        :param sq_dist: Square distance
        :type sq_dist:
        :param trans: Return results in the transformed space.
        :type trans:
        :return: 3D array with the gradient of the kernel function in every
         dimension the length-scale hyper-parameter space.
        :rtype:
        """
        dist = np.sqrt(sq_dist)

        dkr_dov = np.multiply(
                (1.0 + SQRT_5 * dist + (5.0 / 3.0) * sq_dist),
                np.exp(-SQRT_5 * dist)
            ) * \
            2.0 * self.get_param_value('output_variance')

        if trans:
            dkr_dov = self.get_hyperparam('output_variance').grad_trans(
                dkr_dov
            )

        return dkr_dov,

    def dkr_dl(self, sq_dist, dr_dl):
        """
        Measures gradient of the kernel function in the
        hyper-parameter space.

        :param sq_dist: Square distance
        :type sq_dist:
        :param dr_dl:
        :type dr_dl:
        :return: 3D array with the gradient of the kernel function in every
         dimension the length-scale hyper-parameter space.
        :rtype:
        """
        dist = np.sqrt(sq_dist)
        grad_r2 = -(5.0 / 6.0) * np.exp(-SQRT_5 * dist) * (1 + SQRT_5 * dist)
        dkr_dl = grad_r2[:, :, np.newaxis] * \
            dr_dl * np.square(self.get_param_value('output_variance'))

        return dkr_dl
