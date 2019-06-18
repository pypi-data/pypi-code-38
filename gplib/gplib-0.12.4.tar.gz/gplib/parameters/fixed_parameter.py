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

from .parameter import Parameter


class FixedParameter(Parameter):
    """

    """

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
        if optimizable_only:
            return

        super(FixedParameter, self).set_param_values(
            params, optimizable_only=optimizable_only, trans=trans
        )

    def set_params_to_default(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if optimizable_only:
            return

        super(FixedParameter, self).set_params_to_default(
            optimizable_only=optimizable_only
        )

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        pass

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        pass

    def get_param_values(self, optimizable_only=False, trans=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        if optimizable_only:
            return []

        return super(FixedParameter, self).get_param_values(
            optimizable_only=optimizable_only, trans=trans
        )

    def get_param_keys(self, recursive=True, optimizable_only=False):
        """

        :param recursive:
        :type recursive:
        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if optimizable_only:
            return []

        return super(FixedParameter, self).get_param_keys(
            recursive=recursive,
            optimizable_only=optimizable_only
        )

    def get_param_n(self, optimizable_only=False):
        """

        :param optimizable_only:
        :type optimizable_only:
        :return:
        :rtype:
        """
        if optimizable_only:
            return 0

        return super(FixedParameter, self).get_param_n(
            optimizable_only=optimizable_only
        )
