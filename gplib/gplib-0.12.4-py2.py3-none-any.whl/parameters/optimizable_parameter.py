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

from .parameter import Parameter


class OptimizableParameter(Parameter):
    """

    """
    def __init__(self, name, transformation, default_value=1.0, jitter_sd=10.0):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        :param jitter_sd:
        :type jitter_sd:
        """

        super(OptimizableParameter, self).__init__(
            name, transformation, default_value
        )

        self.optimized_value = None

        self.jitter_sd = jitter_sd

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        self.optimized_value = None

        super(OptimizableParameter, self).set_params_to_default(
            optimizable_only=optimizable_only
        )

    def set_params_at_random(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        if self.optimized_value is not None:
            current_value = self.optimized_value
            jitter_sd = self.jitter_sd * 0.1
        else:
            current_value = self.default_value
            jitter_sd = self.jitter_sd

        if trans:
            current_value = self.transformation.trans(current_value)

        current_value += np.array(
            np.random.normal(
                loc=0.0,
                scale=jitter_sd,
                size=self.dims
            )
        )

        self.set_param_values(current_value, trans=trans)

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        self.optimized_value = self.current_value

    def grad_trans(self, df):
        """

        :param df:
        :type df:
        :return:
        :rtype:
        """

        return self.transformation.grad_trans(self.current_value, df)
