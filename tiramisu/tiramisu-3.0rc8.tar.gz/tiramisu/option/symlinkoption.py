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
from typing import Any
from .baseoption import BaseOption, valid_name
from ..i18n import _


class SymLinkOption(BaseOption):
    __slots__ = ('_opt',)

    def __init__(self,
                 name: str,
                 opt: BaseOption) -> None:
        if not valid_name(name):
            raise ValueError(_('"{0}" is an invalid name for an option').format(name))
        if not isinstance(opt, BaseOption) or \
                opt.impl_is_optiondescription() or \
                opt.impl_is_symlinkoption():
            raise ValueError(_('malformed symlinkoption must be an option for symlink {0}'
                               '').format(name))
        _setattr = object.__setattr__
        _setattr(self, '_name', name)
        _setattr(self, '_opt', opt)
        opt._add_dependency(self)
        self._path = None

    def __getattr__(self,
                    name: str) -> Any:
        return getattr(self._opt, name)

    def impl_has_dependency(self,
                            self_is_dep: bool=True) -> bool:
        """If self_is_dep is True, it has dependency (self._opt), so return True
        if self_is_dep is False, cannot has validation or callback, so return False
        """
        return self_is_dep

    def impl_is_symlinkoption(self) -> bool:
        return True

    def impl_getopt(self) -> BaseOption:
        return self._opt

    def get_consistencies(self) -> tuple:
        return ()
