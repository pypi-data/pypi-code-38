# -*- coding: utf-8 -*-
"Leadership support"
# Copyright (C) 2014-2019 Team tiramisu (see AUTHORS for all contributors)
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
import weakref
from itertools import chain
from typing import List, Iterator, Optional, Any


from ..i18n import _
from ..setting import groups, undefined, OptionBag, Settings
from ..value import Values
from .optiondescription import OptionDescription
from .syndynoptiondescription import SynDynLeadership
from .baseoption import BaseOption
from .option import Option
from ..error import RequirementError
from ..function import ParamOption


class Leadership(OptionDescription):
    __slots__ = ('leader',
                 'followers')

    def __init__(self,
                 name: str,
                 doc: str,
                 children: List[BaseOption],
                 requires=None,
                 properties=None) -> None:

        super().__init__(name,
                         doc,
                         children,
                         requires=requires,
                         properties=properties)
        self._group_type = groups.leadership
        followers = []
        if len(children) < 2:
            raise ValueError(_('a leader and a follower are mandatories in leadership "{}"'
                               '').format(name))
        leader = children[0]
        for idx, child in enumerate(children):
            if __debug__:
                if child.impl_is_symlinkoption():
                    raise ValueError(_('leadership "{0}" shall not have '
                                       "a symlinkoption").format(self.impl_get_display_name()))
                if not isinstance(child, Option):
                    raise ValueError(_('leadership "{0}" shall not have '
                                       'a subgroup').format(self.impl_get_display_name()))
                if not child.impl_is_multi():
                    raise ValueError(_('only multi option allowed in leadership "{0}" but option '
                                       '"{1}" is not a multi'
                                       '').format(self.impl_get_display_name(),
                                                  child.impl_get_display_name()))
                if idx != 0 and child.impl_getdefault() != []:
                    raise ValueError(_('not allowed default value for follower option "{0}" '
                                       'in leadership "{1}"'
                                       '').format(child.impl_get_display_name(),
                                                  self.impl_get_display_name()))
            if idx != 0:
                # remove empty property for follower
                child_properties = list(child._properties)
                child_properties.remove('empty')
                child._properties = frozenset(child_properties)
                followers.append(child)
            child._add_dependency(self)
            child._leadership = weakref.ref(self)
        callback, callback_params = leader.impl_get_callback()
        if callback is not None and callback_params is not None:
            for callbk in chain(callback_params.args, callback_params.kwargs.values()):
                if isinstance(callbk, ParamOption) and callbk.option in followers:
                    raise ValueError(_("callback of leader's option shall "
                                       "not refered to a follower's ones"))
        # leader should not have requires, only Leadership should have
        # so move requires to Leadership
        # if Leadership has requires too, cannot manage this move so raises
        leader_requires = getattr(leader, '_requires', None)
        if leader_requires:
            if __debug__ and self.impl_getrequires():
                raise RequirementError(_('leader {} have requirement, but Leadership {} too'
                                         '').format(leader.impl_getname(),
                                                    self.impl_getname()))
            leader_calproperties = getattr(leader, '_calc_properties', None)
            if leader_calproperties:
                if __debug__ and properties is not None:
                    self.validate_properties(name, leader_calproperties, frozenset(properties))
                setattr(self, '_calc_properties', leader_calproperties)
                setattr(self, '_requires', leader_requires)
                delattr(leader, '_requires')
        if __debug__:
            for requires_ in getattr(self, '_requires', ()):
                for require in requires_:
                    for require_opt, values in require[0]:
                        if not isinstance(require_opt, tuple) and require_opt.impl_is_multi() and require_opt.impl_get_leadership():
                            raise ValueError(_('malformed requirements option "{0}" '
                                               'must not be in follower for "{1}"').format(
                                                   require_opt.impl_getname(),
                                                   self.impl_getname()))

    def is_leader(self,
                  opt: Option) -> bool:
        leader = self.get_leader()
        return opt == leader or (opt.impl_is_dynsymlinkoption() and opt.opt == leader)

    def get_leader(self) -> Option:
        return self._children[1][0]

    def get_followers(self) -> Iterator[Option]:
        for follower in self._children[1][1:]:
            yield follower

    def in_same_group(self,
                      opt: Option) -> bool:
        if opt.impl_is_dynsymlinkoption():
            opt = opt.opt
        return opt in self._children[1]

    def reset(self,
              values: Values,
              option_bag: OptionBag,
              _commit: bool=True) -> None:
        config_bag = option_bag.config_bag.copy()
        config_bag.remove_validation()
        for follower in self.get_followers():
            follower_path = follower.impl_getpath()
            soption_bag = OptionBag()
            soption_bag.set_option(follower,
                                   follower_path,
                                   None,
                                   config_bag)
            values.reset(soption_bag,
                         _commit=_commit)

    def pop(self,
            values: Values,
            index: int,
            option_bag: OptionBag,
            followers: Optional[List[Option]]=undefined) -> None:
        if followers is undefined:
            # followers are not undefined only in SynDynLeadership
            followers = self.get_followers()
        config_bag = option_bag.config_bag.copy()
        config_bag.remove_validation()
        for follower in followers:
            follower_path = follower.impl_getpath()
            followerlen = values._p_.get_max_length(follower_path)
            soption_bag = OptionBag()
            soption_bag.set_option(follower,
                                   follower_path,
                                   index,
                                   config_bag)
            # do not check force_default_on_freeze or force_metaconfig_on_freeze
            soption_bag.properties = set()
            if not values.is_default_owner(soption_bag,
                                           validate_meta=False) and followerlen > index:
                values._p_.resetvalue_index(follower_path,
                                            index,
                                            True)
            if followerlen > index + 1:
                for idx in range(index + 1, followerlen):
                    if values._p_.hasvalue(follower_path, idx):
                        values._p_.reduce_index(follower_path,
                                                idx)

    def reset_cache(self,
                    path: str,
                    values: Values,
                    settings: Settings,
                    resetted_opts: List[Option]) -> None:
        self._reset_cache(path,
                          self.get_leader(),
                          self.get_followers(),
                          values,
                          settings,
                          resetted_opts)

    def _reset_cache(self,
                     path: str,
                     leader: Option,
                     followers: List[Option],
                     values: Values,
                     settings: Settings,
                     resetted_opts: List[Option]) -> None:
        super().reset_cache(path,
                            values,
                            settings,
                            resetted_opts)
        leader.reset_cache(leader.impl_getpath(),
                           values,
                           settings,
                           None)
        for follower in followers:
            spath = follower.impl_getpath()
            follower.reset_cache(spath,
                                 values,
                                 settings,
                                 None)
            resetted_opts.append(spath)

    def impl_is_leadership(self) -> None:
        return True

    def to_dynoption(self,
                     rootpath: str,
                     suffix: str) -> SynDynLeadership:
        return SynDynLeadership(self,
                                rootpath,
                                suffix)
