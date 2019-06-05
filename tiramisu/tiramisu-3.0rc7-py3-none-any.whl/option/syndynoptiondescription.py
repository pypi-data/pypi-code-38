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
from typing import Optional, Iterator, Union, Any, List


from ..i18n import _
from ..setting import ConfigBag, groups, undefined, Settings
from ..value import Values
from .baseoption import BaseOption
from .syndynoption import SynDynOption


class SynDynOptionDescription:
    __slots__ = ('_opt',
                 '_subpath',
                 '_suffix')

    def __init__(self,
                 opt: BaseOption,
                 subpath: str,
                 suffix: str) -> None:
        self._opt = opt
        self._subpath = subpath
        self._suffix = suffix

    def __getattr__(self,
                    name: str) -> Any:
        # if not in SynDynOptionDescription, get value in self._opt
        return getattr(self._opt,
                       name)

    def impl_getopt(self) -> BaseOption:
        return self._opt

    def get_child(self,
                  name: str,
                  config_bag: ConfigBag,
                  subpath: str) -> BaseOption:
    #FIXME -> Union[BaseOption, SynDynOptionDescription]:
        if name.endswith(self._suffix):
            oname = name[:-len(self._suffix)]
            try:
                child = self._children[1][self._children[0].index(oname)]
            except ValueError:
                # when oname not in self._children
                pass
            else:
                return child.to_dynoption(subpath,
                                          self._suffix)
        raise AttributeError(_('unknown option "{0}" '
                               'in syndynoptiondescription "{1}"'
                               '').format(name, self.impl_getname()))

    def impl_getname(self) -> str:
        return self._opt.impl_getname() + self._suffix

    def impl_is_dynoptiondescription(self) -> bool:
        return True

    def get_children(self,
                     config_bag: ConfigBag,
                     dyn: bool=True):
        subpath = self.impl_getpath()
        for child in self._opt.get_children(config_bag):
            yield child.to_dynoption(subpath,
                                     self._suffix)

    def get_children_recursively(self,
                                 bytype: Optional[BaseOption],
                                 byname: Optional[str],
                                 config_bag: ConfigBag,
                                 self_opt: BaseOption=None) -> BaseOption:
    # FIXME -> Iterator[Union[BaseOption, SynDynOptionDescription]]:
        return self._opt.get_children_recursively(bytype,
                                                  byname,
                                                  config_bag,
                                                  self)
         
    def impl_getpath(self) -> str:
        subpath = self._subpath
        if subpath != '':
            subpath += '.'
        return subpath + self.impl_getname()

    def impl_get_display_name(self) -> str:
        return self._opt.impl_get_display_name() + self._suffix


class SynDynLeadership(SynDynOptionDescription):
    def get_leader(self) -> SynDynOption:
        return self._opt.get_leader().to_dynoption(self.impl_getpath(),
                                                   self._suffix)

    def get_followers(self) -> Iterator[SynDynOption]:
        subpath = self.impl_getpath()
        for follower in self._opt.get_followers():
            yield follower.to_dynoption(subpath,
                                        self._suffix)

    def reset_cache(self,
                    path: str,
                    values: Values,
                    settings: Settings,
                    resetted_opts: List[str]) -> None:
        leader = self.get_leader()
        followers = self.get_followers()
        self._reset_cache(path,
                          leader,
                          followers,
                          values,
                          settings,
                          resetted_opts)

    def pop(self,
            *args,
            **kwargs) -> None:
        self._opt.pop(*args,
                      followers=self.get_followers(),
                      **kwargs)
