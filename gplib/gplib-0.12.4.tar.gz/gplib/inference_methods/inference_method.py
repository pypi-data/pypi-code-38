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

from ..cache import CachedMethod


class InferenceMethod(object):
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

    def marginalize_gp(self, data_x, data_y=None):
        """

        :param data_x:
        :type data_x:
        :param data_y:
        :type data_y:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def loocv(self, data_x, data_y=None):
        """

        :param data_x:
        :type data_x:
        :param data_y:
        :type data_y:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    @staticmethod
    @CachedMethod()
    def safe_chol(k_matrix):
        """
        Compute cholesky decomposition

        :param k_matrix:
        :type k_matrix:
        :return:
        :rtype:
        """

        # Non finite values in covariance matrix
        if not np.all(np.isfinite(k_matrix)):
            raise np.linalg.LinAlgError("Non finite values in cov matrix")

        # Covariance matrix is not symmetric
        if np.max(np.abs(k_matrix - k_matrix.T)) > 1e-20:
            raise np.linalg.LinAlgError("Covariance matrix is not symmetric")

        # Solve cholesky decomposition
        l_matrix = None
        jitter = 1e-30
        max_jitter = 1e-6
        k_corrected = k_matrix
        while l_matrix is None and jitter < max_jitter:
            l_matrix, error = scipy.linalg.lapack.dpotrf(
                np.ascontiguousarray(k_corrected),
                lower=1
            )
            if error != 0:
                l_matrix = None
                k_corrected = k_matrix + jitter * np.eye(k_matrix.shape[0])
                jitter *= 10

        if l_matrix is None:
            raise np.linalg.LinAlgError("Can't compute cholesky decomposition")

        # Non finite values in L matrix
        if not np.all(np.isfinite(l_matrix)):
            raise np.linalg.LinAlgError("Non finite values in L matrix")

        # Main diagonal of L not positive
        if np.min(np.diagonal(l_matrix)) <= 0.0:
            raise np.linalg.LinAlgError("Main diagonal of L not positive")

        # Errors in L matrix multiplication
        if np.max(np.abs(k_corrected - np.dot(l_matrix, l_matrix.T))) > 1e-10:
            raise np.linalg.LinAlgError("Errors in L matrix multiplication")

        return l_matrix
