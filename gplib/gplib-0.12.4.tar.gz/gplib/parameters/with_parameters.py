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


class WithParameters(Parametrizable):
    """

    """
    def __init__(self, hyperparameters):
        """

        :param hyperparameters:
        :type hyperparameters:
        """
        self.hyperparameters = hyperparameters

    def is_array(self):
        """

        :return:
        :rtype:
        """

        return True

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

        assert (len(params) == self.get_param_n(
            optimizable_only=optimizable_only)),\
            "length of params is not correct"

        i = 0
        for hyperparameter in self.hyperparameters:
            number_of_params = \
                hyperparameter.get_param_n(optimizable_only=optimizable_only)
            param_slice = slice(i, i + number_of_params)
            hyperparameter.set_param_values(
                params[param_slice],
                optimizable_only=optimizable_only,
                trans=trans
            )
            i += number_of_params

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.set_params_to_default(
                optimizable_only=optimizable_only
            )

    def set_params_at_random(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.set_params_at_random(trans)

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.save_current_as_optimized()

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        params = []
        for hyperparameter in self.hyperparameters:
            params += hyperparameter.get_param_values(
                optimizable_only=optimizable_only,
                trans=trans
            )

        return params

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
            return self.__class__.__name__

        params = []

        for hyperparameter in self.hyperparameters:
            name = self.__class__.__name__
            params += [
                name + "_" + item for item in hyperparameter.get_param_keys(
                    optimizable_only=optimizable_only
                )
            ]

        return params

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """

        n_optimizable = 0

        for hyperparameter in self.hyperparameters:
            n_optimizable += hyperparameter.get_param_n(
                optimizable_only=optimizable_only
            )

        return n_optimizable

    def get_hyperparams(self):
        """

        :return:
        :rtype:
        """

        return self.hyperparameters

    def set_hyperparams(self, hyperparams):
        """

        :param hyperparams:
        :type hyperparams:
        :return:
        :rtype:
        """

        assert type(hyperparams) is list,\
            "hyperparams must be a list"
        self.hyperparameters = hyperparams

    def get_hyperparam(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        for hyperparameter in self.hyperparameters:
            hp_name = hyperparameter.get_param_keys(
                recursive=False,
                optimizable_only=False
            )
            if name == hp_name:
                return hyperparameter

    def get_param_value(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        hyperparam = self.get_hyperparam(name)

        value = hyperparam.get_param_values(optimizable_only=False)

        if hyperparam.is_array():
            return value

        return value[0]
