# -*- coding: utf-8 -*-
# Copyright (C) 2017-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The original `Config` design model is unproudly borrowed from
# the rough pypy's guys: http://codespeak.net/svn/pypy/dist/pypy/config/
# the whole pypy projet is under MIT licence
# ____________________________________________________________
from types import FunctionType

from ..setting import undefined
from ..i18n import _
from .option import Option
from ..autolib import carry_out_calculation
from ..error import ConfigError, display_list


class ChoiceOption(Option):
    """represents a choice out of several objects.

    The option can also have the value ``None``
    """
    __slots__ = tuple()
    _type = 'choice'
    _display_name = _('choice')

    def __init__(self,
                 name,
                 doc,
                 values,
                 default=None,
                 values_params=None,
                 default_multi=None,
                 requires=None,
                 multi=False,
                 callback=None,
                 callback_params=None,
                 validator=None,
                 validator_params=None,
                 properties=None,
                 warnings_only=False):

        """
        :param values: is a list of values the option can possibly take
        """
        if isinstance(values, FunctionType):
            values_params = self._build_calculator_params(values,
                                                          values_params,
                                                          'values')
            if values_params:
                self._choice_values_params = values_params
        else:
            if values_params is not None:
                raise ValueError(_('values is not a function, so values_params must be None'))
            if not isinstance(values, tuple):
                raise TypeError(_('values must be a tuple or a function for {0}'
                                 ).format(name))
        self._choice_values = values
        super(ChoiceOption, self).__init__(name,
                                           doc,
                                           default=default,
                                           default_multi=default_multi,
                                           callback=callback,
                                           callback_params=callback_params,
                                           requires=requires,
                                           multi=multi,
                                           validator=validator,
                                           validator_params=validator_params,
                                           properties=properties,
                                           warnings_only=warnings_only)

    def impl_get_values(self,
                        option_bag,
                        current_opt=undefined):
        if current_opt is undefined:
            current_opt = self
        values = self._choice_values
        if isinstance(values, FunctionType):
            if option_bag is undefined:
                values = undefined
            else:
                values = carry_out_calculation(current_opt,
                                               callback=values,
                                               callback_params=getattr(self, '_choice_values_params', {}),
                                               index=None,
                                               config_bag=option_bag.config_bag,
                                               fromconsistency=[])
                if values is not undefined and not isinstance(values, list):
                    raise ConfigError(_('calculated values for {0} is not a list'
                                        '').format(self.impl_getname()))
        return values


    def _validate(self,
                  value,
                  option_bag,
                  current_opt=undefined):
        values = self.impl_get_values(option_bag,
                                      current_opt=current_opt)
        if values is not undefined and value not in values:
            if len(values) == 1:
                raise ValueError(_('only "{0}" is allowed'
                                   '').format(values[0]))
            else:
                raise ValueError(_('only {0} are allowed'
                                   '').format(display_list(values, add_quote=True)))
