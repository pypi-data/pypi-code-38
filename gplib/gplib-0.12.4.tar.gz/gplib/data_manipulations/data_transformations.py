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


class DataTransformation(object):
    """

    """

    def __init__(self, data):

        self.transform_matrices_dict = {
            key: DataTransformation._get_transform_matrices(value)
            for key, value in data.items()
        }

    @staticmethod
    def _get_transform_matrices(matrix):
        """

        :param matrix:
        :type matrix:
        :return:
        :rtype:
        """
        min_x = np.min(matrix, axis=0)
        scale_inv = np.max(matrix, axis=0) - min_x
        scale = np.power(scale_inv, -1)
        scale_inv = np.diag(scale_inv)
        scale = np.diag(scale)
        translate_inv = min_x
        translate = -np.dot(min_x, scale)
        return np.vstack((scale, translate)), \
            np.vstack((scale_inv, translate_inv))

    def transform(self, data, inv=False):
        """

        :param data:
        :type data:
        :param transform:
        :type transform:
        :param inv:
        :type inv:
        :return:
        :rtype:
        """

        return {
            key: self.transform_key(value, key, inv)
            for key, value in data.items()
        }

    def scale(self, data, inv=False):
        """

        :param data:
        :type data:
        :param transform:
        :type transform:
        :param inv:
        :type inv:
        :return:
        :rtype:
        """

        return {
            key: self.scale_key(value, key, inv)
            for key, value in data.items()
        }

    def transform_key(self, matrix, key, inv=False):
        """

        :param matrix:
        :type matrix:
        :param key:
        :type key:
        :param inv:
        :type inv:
        :return:
        :rtype:
        """

        return np.dot(
            np.hstack((matrix, np.ones((len(matrix), 1)))),
            self.transform_matrices_dict[key][1 if inv else 0]
        )

    def scale_key(self, matrix, key, inv=False):
        """

        :param matrix:
        :type matrix:
        :param key:
        :type key:
        :param inv:
        :type inv:
        :return:
        :rtype:
        """

        return np.dot(
            matrix,
            self.transform_matrices_dict[key][1 if inv else 0][:-1]
        )
