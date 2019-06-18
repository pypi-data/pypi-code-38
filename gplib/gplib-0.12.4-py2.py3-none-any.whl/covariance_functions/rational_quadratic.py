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


class RationalQuadratic(StationaryFunction):
    """

    """
    def __init__(self, ov2=1.0, alpha=2.0, ls=None, ard_dims=None):
        hyperparams = [
            OptimizableParameter(
                'output_variance', LogParameterTransformation,
                default_value=ov2
            ),
            OptimizableParameter(
                'alpha', LogParameterTransformation,
                default_value=alpha
            )
        ]

        super(RationalQuadratic, self).__init__(hyperparams, ls, ard_dims)

    def stationary_function(self, sq_dist):
        """
        It applies the Rational Quadratic kernel function
        element-wise to the distance matrix.

        .. math::
            k_{RQ}(r)=(1+\dfrac{1}{2*\alpha}(\dfrac{r}{l})^2)^{-\alpha}

        :param sq_dist: Distance matrix
        :type sq_dist:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """
        return np.power(
                1.0 + (1.0/(2.0*self.get_param_value('alpha'))) * sq_dist,
                -self.get_param_value('alpha')
            ) * np.square(self.get_param_value('output_variance'))

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
        # TODO test this
        return -0.5 * dr_dx * \
            np.square(self.get_param_value('output_variance')) * \
            np.power(
                (1.0 + (1.0/(2.0*self.get_param_value('alpha'))) * sq_dist),
                -self.get_param_value('alpha')-1.0
            )[:, :, np.newaxis]

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
        division = (1.0 / (2.0 * self.get_param_value('alpha'))) * sq_dist

        power = np.power(
                1.0 + division,
                -self.get_param_value('alpha')
            )

        dkr_dov = 2.0 * power * self.get_param_value('output_variance')

        dkr_dalpha = np.square(self.get_param_value('output_variance')) * \
            power * ((division / (division + 1.0)) - np.log(division + 1.0))

        if trans:
            dkr_dov = self.get_hyperparam('output_variance').grad_trans(
                dkr_dov
            )
            dkr_dalpha = self.get_hyperparam('alpha').grad_trans(
                dkr_dalpha
            )

        return dkr_dov, dkr_dalpha

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
        division = (1.0 / (2.0 * self.get_param_value('alpha'))) * sq_dist
        dkr_dl = -0.5 * dr_dl * np.square(self.get_param_value('output_variance')) * \
            np.power(
                1.0 + division,
                -self.get_param_value('alpha')-1.0
            )[:, :, np.newaxis]

        return dkr_dl
