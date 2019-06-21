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
import sys
from typing import Any

from ..setting import undefined, Undefined, OptionBag
from ..i18n import _
from .option import Option


class StrOption(Option):
    "represents the choice of a string"
    __slots__ = tuple()
    _type = 'string'
    _display_name = _('string')

    def _validate(self,
                  value: str,
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        if not isinstance(value, str):
            raise ValueError()


#UnicodeOption is same as StrOption
UnicodeOption = StrOption


class RegexpOption(StrOption):
    __slots__ = tuple()

    def _validate(self,
                  value: Any,
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        super()._validate(value, option_bag, current_opt)
        match = self._regexp.search(value)
        if not match:
            raise ValueError()
