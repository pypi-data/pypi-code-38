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
import sys
from typing import Union

from ..setting import undefined, Undefined, OptionBag
from ..i18n import _
from .option import Option
from .stroption import StrOption


class PortOption(StrOption):
    """represents the choice of a port
    The port numbers are divided into three ranges:
    the well-known ports,
    the registered ports,
    and the dynamic or private ports.
    You can actived this three range.
    Port number 0 is reserved and can't be used.
    see: http://en.wikipedia.org/wiki/Port_numbers
    """
    __slots__ = tuple()
    port_re = re.compile(r"^[0-9]*$")
    _type = 'port'
    _display_name = _('port')

    def __init__(self,
                 name,
                 doc,
                 default=None,
                 default_multi=None,
                 requires=None,
                 multi=False,
                 callback=None,
                 callback_params=None,
                 validator=None,
                 validator_params=None,
                 properties=None,
                 allow_range=False,
                 allow_zero=False,
                 allow_wellknown=True,
                 allow_registred=True,
                 allow_private=False,
                 warnings_only=False):

        extra = {'_allow_range': allow_range,
                 '_min_value': None,
                 '_max_value': None}
        ports_min = [0, 1, 1024, 49152]
        ports_max = [0, 1023, 49151, 65535]
        is_finally = False
        for index, allowed in enumerate([allow_zero,
                                         allow_wellknown,
                                         allow_registred,
                                         allow_private]):
            if extra['_min_value'] is None:
                if allowed:
                    extra['_min_value'] = ports_min[index]
            elif not allowed:
                is_finally = True
            elif allowed and is_finally:
                raise ValueError(_('inconsistency in allowed range'))
            if allowed:
                extra['_max_value'] = ports_max[index]

        if extra['_max_value'] is None:
            raise ValueError(_('max value is empty'))

        super(PortOption, self).__init__(name,
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
                                         warnings_only=warnings_only,
                                         extra=extra)

    def _validate(self,
                  value: Union[int,str],
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        if not isinstance(value, str):
            raise ValueError(_('invalid string'))
        if self.impl_get_extra('_allow_range') and ":" in str(value):
            value = str(value).split(':')
            if len(value) != 2:
                raise ValueError(_('range must have two values only'))
            if not value[0] < value[1]:
                raise ValueError(_('first port in range must be'
                                   ' smaller than the second one'))
        else:
            value = [value]

        for val in value:
            if not self.port_re.search(val):
                raise ValueError()
            val = int(val)
            if not self.impl_get_extra('_min_value') <= val <= self.impl_get_extra('_max_value'):
                raise ValueError(_('must be an integer between {0} '
                                   'and {1}').format(self.impl_get_extra('_min_value'),
                                                     self.impl_get_extra('_max_value')))
