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
from ..cache import CachedMethod


class StationaryFunction(CovarianceFunction):
    """

    """
    def __init__(self, hyperparams, ls=None, ard_dims=None):
        if ard_dims is not None:
            default_lengthscale = np.ones(ard_dims).tolist()
        else:
            default_lengthscale = 1.0

        if ls is not None:
            default_lengthscale *= ls

        hyperparams.append(OptimizableParameter(
            'lengthscale', LogParameterTransformation,
            default_value=default_lengthscale,
        ))

        super(StationaryFunction, self).__init__(hyperparams)

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
        sq_dist = self.sq_distance(
            mat_a, mat_b=mat_b,
            only_diagonal=only_diagonal
        )

        return self.stationary_function(sq_dist)

    def dk_dx(self, mat_a, mat_b=None):
        """
        Measures gradient of the distance between solutions of A and B in X.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :return: 3D array with the gradient in every dimension of X.
        :rtype:
        """
        if mat_b is None:
            mat_b = mat_a

        dr_dx = np.zeros((mat_a.shape[0], mat_b.shape[0], mat_a.shape[1]))

        for i in range(0, mat_a.shape[0]):
            dr_dx[i, :, :] = 2.0 * (mat_a[i, :] - mat_b[:, :]) / \
                              np.power(self.get_param_value('lengthscale'), 2.0)

        # TODO if covariance is needed along with dk_dx, this is computed twice
        sq_dist = self.sq_distance(mat_a, mat_b=mat_b)
        return self.dkr_dx(sq_dist, dr_dx)

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
        if mat_b is None:
            mat_b = mat_a

        # TODO if covariance is needed along with dk_dx, this is computed twice
        sq_dist = self.sq_distance(mat_a, mat_b=mat_b)
        result = self.dkr_dtheta(sq_dist, trans)

        dr_dl = np.zeros((mat_a.shape[0], mat_b.shape[0], mat_a.shape[1]))
        for i in range(0, mat_a.shape[0]):
            dr_dl[i, :, :] = - 2.0 * (
                np.power(mat_a[i, :] - mat_b[:, :], 2.0)) / \
                    np.power(self.get_param_value('lengthscale'), 3.0)

        dkr_dl = self.dkr_dl(sq_dist, dr_dl)

        if trans:
            dkr_dl = self.get_hyperparam('lengthscale').grad_trans(
                dkr_dl
            )

        l_len = self.get_hyperparam('lengthscale').get_param_n(
            optimizable_only=False
        )

        if l_len == 1:
            result += np.sum(dkr_dl, axis=2),
        elif l_len > 1:
            for i in range(l_len):
                result += dkr_dl[:, :, i],
        else:
            raise Exception("lengthscale array length not valid")

        return result

    def sq_distance(self, mat_a, mat_b=None, only_diagonal=False):
        """
        Measures the distance matrix between solutions of A and B.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :return: Distance matrix between solutions of A and B.
        :rtype:
        """
        lengthscale = self.get_hyperparam('lengthscale')
        if lengthscale.is_array():
            mat_a = mat_a / lengthscale.get_param_values()
            if mat_b is not None:
                mat_b = mat_b / lengthscale.get_param_values()

        r2 = StationaryFunction.static_sq_distance(
            mat_a, mat_b=mat_b,
            only_diagonal=only_diagonal
        )

        if not lengthscale.is_array():
            r2 = r2 / np.square(lengthscale.get_param_values()[0])
        return r2

    @staticmethod
    @CachedMethod()
    def static_sq_distance(mat_a, mat_b=None, only_diagonal=False):
        """
        Measures the square euclidean distance between solutions of A and B.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :return: Distance matrix between solutions of A and B.
        :rtype:
        """

        if mat_b is None:
            if only_diagonal:
                return np.zeros((len(mat_a), 1))
            center = np.mean(mat_a, axis=0)
            mat_a = mat_a - center
            mat_a_sq = np.sum(np.square(mat_a), 1)

            r2 = mat_a_sq[:, None] + mat_a_sq[None, :]

            r2 -= 2. * np.dot(mat_a, mat_a.T)

            np.lib.stride_tricks.as_strided(
                r2, shape=(r2.shape[0], ),
                strides=((r2.shape[0] + 1) * r2.itemsize, )
            )[:, ] = 0
        else:
            center = np.mean(np.vstack((mat_a, mat_b)), axis=0)
            mat_a = mat_a - center
            mat_b = mat_b - center
            mat_a_sq = np.sum(np.square(mat_a), 1)
            mat_b_sq = np.sum(np.square(mat_b), 1)

            r2 = mat_a_sq[:, None] + mat_b_sq[None, :]

            r2 -= 2. * np.dot(mat_a, mat_b.T)
        r2 = r2.clip(min=0.0)

        return r2

    def stationary_function(self, sq_dist):
        """
        It applies the kernel function
        element-wise to the distance matrix.

        :param sq_dist: Distance matrix
        :type sq_dist:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

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

        raise NotImplementedError("Not Implemented. This is an interface.")

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

        raise NotImplementedError("Not Implemented. This is an interface.")

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

        raise NotImplementedError("Not Implemented. This is an interface.")
