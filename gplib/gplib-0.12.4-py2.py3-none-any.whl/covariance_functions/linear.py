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

from .dot_product_function import DotProductFunction


class Linear(DotProductFunction):
    """

    """
    def __init__(self, ls=None, shift=None, ard_dims=None):
        hyperparams = []

        super(Linear, self).__init__(hyperparams, ls, shift, ard_dims)

    def dot_product_function(self, dot_product):
        """

        :param dot_product:
        :type dot_product:
        :return:
        :rtype:
        """

        return dot_product
