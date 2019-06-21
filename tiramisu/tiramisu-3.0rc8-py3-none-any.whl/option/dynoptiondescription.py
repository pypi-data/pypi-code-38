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
import re
from typing import List, Callable


from ..i18n import _
from .optiondescription import OptionDescription
from .baseoption import BaseOption
from ..setting import ConfigBag, groups, undefined
from ..error import ConfigError
from ..autolib import carry_out_calculation


NAME_REGEXP = re.compile(r'^[a-zA-Z\d\-_]*$')


class DynOptionDescription(OptionDescription):

    def __init__(self,
                 name: str,
                 doc: str,
                 children: List[BaseOption],
                 requires=None,
                 properties=None,
                 callback: Callable=None,
                 callback_params=None) -> None:

        super().__init__(name,
                         doc,
                         children,
                         requires,
                         properties)
        # check children + set relation to this dynoptiondescription
        for child in children:
            if isinstance(child, OptionDescription):
                if __debug__ and child.impl_get_group_type() != groups.leadership:
                    raise ConfigError(_('cannot set optiondescription in a '
                                        'dynoptiondescription'))
                for chld in child.get_children(config_bag=undefined):
                    chld._setsubdyn(self)
            if __debug__ and child.impl_is_symlinkoption():
                raise ConfigError(_('cannot set symlinkoption in a '
                                    'dynoptiondescription'))
            child._setsubdyn(self)
        # add callback
        self._impl_set_callback(callback,
                                callback_params)

    def _validate_calculator(self,
                             callback: Callable,
                             callback_params) -> None:
        if callback is None:
            raise ConfigError(_('callback is mandatory for the dynoptiondescription "{}"'
                                '').format(self.impl_get_display_name()))

    def get_suffixes(self,
                     config_bag: ConfigBag,
                     remove_none: bool=False) -> List[str]:
        callback, callback_params = self.impl_get_callback()
        values = carry_out_calculation(self,
                                       callback,
                                       callback_params,
                                       None,
                                       config_bag,
                                       fromconsistency=[])
        if not isinstance(values, list):
            raise ValueError(_('DynOptionDescription callback for option "{}", is not a list ({})'
                               '').format(self.impl_get_display_name(), values))
        values_ = []
        for val in values:
            if not isinstance(val, str) or re.match(NAME_REGEXP, val) is None:
                if not remove_none or val is not None:
                    raise ValueError(_('invalid suffix "{}" for option "{}"'
                                       '').format(val,
                                                  self.impl_get_display_name()))
            else:
                values_.append(val)
        if len(values_) > len(set(values_)):
            extra_values = values_.copy()
            for val in set(values_):
                extra_values.remove(val)
            raise ValueError(_('DynOptionDescription callback return a list with multiple value '
                               '"{}"''').format(extra_values))
        return values_

    def impl_is_dynoptiondescription(self) -> bool:
        return True
