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

from .parametrizable import Parametrizable


class Parameter(Parametrizable):
    """

    """
    def __init__(self, name, transformation, default_value):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        """

        self.name = name
        self.transformation = transformation
        self.default_value = default_value
        self.array = hasattr(self.default_value, "__len__")
        self.current_value = self.default_value

        self.dims = 1
        if self.array:
            self.dims = len(self.default_value)

    def is_array(self):
        """

        :return:
        :rtype:
        """
        return self.array

    def set_param_values(self, params, optimizable_only=False, trans=False):
        """

        :param params:
        :type params:
        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        assert len(params) == self.dims, \
            "length of {} is not correct".format(self.name)

        if trans:
            if self.array:
                params = self.transformation.inv_trans(params).tolist()
            else:
                params = self.transformation.inv_trans(params)

        if self.array is False:
            self.current_value = params[0]
        else:
            self.current_value = params

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        self.current_value = self.default_value

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        assert self.current_value is not None, \
            "{} has not been initialized".format(self.name)

        current_value = self.current_value
        if trans:
            current_value = self.transformation.trans(current_value)
            if self.array:
                current_value = current_value.tolist()

        if self.array:
            return current_value
        return [current_value]

    def get_param_keys(self, recursive=True, optimizable_only=False):
        """

        :param recursive:
        :type recursive:
        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if not recursive:
            return self.name

        if self.dims == 1:
            return [self.name]

        return [
            "{}_d{}".format(self.name, dim) for dim in range(self.dims)
        ]

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        return self.dims
