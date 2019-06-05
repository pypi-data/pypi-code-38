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
# ____________________________________________________________
from inspect import ismethod, getdoc, signature
from time import time
from typing import List, Set, Any, Optional, Callable, Union, Dict


from .error import APIError, ConfigError, LeadershipError, PropertiesOptionError
from .i18n import _
from .setting import ConfigBag, OptionBag, owners, groups, Undefined, undefined, \
                     FORBIDDEN_SET_PROPERTIES, SPECIAL_PROPERTIES, EXPIRATION_TIME
from .config import KernelConfig, SubConfig, KernelGroupConfig, KernelMetaConfig, KernelMixConfig
from .option import ChoiceOption, RegexpOption, OptionDescription
from .todict import TiramisuDict


TIRAMISU_VERSION = 3


class TiramisuHelp:
    _tmpl_help = '    {0}\t{1}'

    def help(self,
             _display: bool=True) -> List[str]:
        def display(doc=''):
            if _display: # pragma: no cover
                print(doc)
        options = []
        all_modules = dir(self)
        modules = []
        max_len = 0
        force = False
        for module_name in all_modules:
            if module_name in ['forcepermissive', 'unrestraint']:
                force = True
                max_len = max(max_len, len('forcepermissive'))
            elif module_name is not 'help' and not module_name.startswith('_'):
                modules.append(module_name)
                max_len = max(max_len, len(module_name))
        modules.sort()

        display(_(getdoc(self)))
        display()
        if force:
            display(_('Settings:'))
            display(self._tmpl_help.format('forcepermissive', _('Access to option without verifying permissive properties')).expandtabs(max_len + 10))
            display(self._tmpl_help.format('unrestraint', _('Access to option without property restriction')).expandtabs(max_len + 10))
            display()
        if isinstance(self, TiramisuDispatcher):
            doc = _(getdoc(self.__call__))
            display(_('Call: {}').format(doc))
            display()
        display(_('Commands:'))
        for module_name in modules:
            module = getattr(self, module_name)
            doc = _(getdoc(module))
            display(self._tmpl_help.format(module_name, doc).expandtabs(max_len + 10))
        display()

    def __dir__(self):
        if '_registers' in super().__dir__():
            return list(self._registers.keys())
        return super().__dir__()


class CommonTiramisu(TiramisuHelp):
    _allow_optiondescription = True
    _validate_properties = True

    def _get_option(self) -> Any:
        option = self._option_bag.option
        if option is None:
            option = self._subconfig.cfgimpl_get_description().get_child(self._name,
                                                                         self._option_bag.config_bag,
                                                                         self._subconfig.cfgimpl_get_path())
            option_bag = OptionBag()
            option_bag.set_option(option,
                                  self._option_bag.path,
                                  self._option_bag.index,
                                  self._option_bag.config_bag)
            if self._validate_properties:
                option_bag.config_bag.context.cfgimpl_get_settings().validate_properties(option_bag)
            self._option_bag = option_bag
            index = self._option_bag.index
            if index is not None:
                if option.impl_is_optiondescription() or not option.impl_is_follower():
                    raise APIError('index must be set only with a follower option')
                self._length = self._subconfig.cfgimpl_get_length_leadership(self._option_bag)
                if index >= self._length:
                    raise LeadershipError(_('index "{}" is higher than the leadership length "{}" '
                                            'for option "{}"').format(index,
                                                                      self._length,
                                                                      option.impl_get_display_name()))
            if not self._allow_optiondescription and option.impl_is_optiondescription():
                raise APIError(_('option must not be an optiondescription'))
        return option


class CommonTiramisuOption(CommonTiramisu):
    _allow_optiondescription = False
    _follower_need_index = True
    _validate_properties = False

    def __init__(self,
                 name: str,
                 subconfig: Union[KernelConfig, SubConfig],
                 option_bag: OptionBag) -> None:
        self._option_bag = option_bag
        self._name = name
        self._subconfig = subconfig
        # for help()
        if option_bag is not None and self._option_bag.config_bag.context.impl_type != 'group':
            self._get_option()
            if option_bag.config_bag is not None and self._follower_need_index:
                self._test_follower_index()

    def _test_follower_index(self) -> None:
        option = self._option_bag.option
        if not option.impl_is_optiondescription() and \
                self._option_bag.index is None and \
                option.impl_is_follower():
            raise APIError(_('index must be set with the follower option "{}"').format(self._option_bag.path))

    def __getattr__(self, name):
        raise APIError(_('unknown method {}').format(name))


class _TiramisuOptionOptionDescription(CommonTiramisuOption):
    """Manage option"""
    _allow_optiondescription = True
    _follower_need_index = False

    def get(self):
        """Get Tiramisu option"""
        return self._option_bag.option

    def type(self):
        return self._option_bag.option.get_type()

    def isleadership(self):
        """Test if option is a leader or a follower"""
        option = self._option_bag.option
        return option.impl_is_leadership()

    def doc(self):
        """Get option document"""
        option = self._option_bag.option
        return option.impl_get_display_name()

    def name(self,
             follow_symlink: bool=False) -> str:
        """Get option name"""
        if not follow_symlink or \
                self.isoptiondescription() or \
                not self.issymlinkoption():
            return self._name
        else:
            option = self._option_bag.option
            return option.impl_getopt().impl_getname()

    def path(self) -> str:
        """Get option path"""
        return self._option_bag.path

    def has_dependency(self, self_is_dep=True):
        """Test if option has dependency"""
        option = self._option_bag.option
        return option.impl_has_dependency(self_is_dep)

    def requires(self):
        """Get requires for an option"""
        option = self._option_bag.option
        return option.impl_getrequires()

    def isoptiondescription(self):
        """Test if option is an optiondescription"""
        option = self._option_bag.option
        return option.impl_is_optiondescription()

    def properties(self,
                   only_raises=False):
        """Get properties for an option"""
        settings = self._option_bag.config_bag.context.cfgimpl_get_settings()
        properties = settings.getproperties(self._option_bag,
                                            apply_requires=False)
        if not only_raises:
            return properties
        # do not check cache properties/permissives which are not save (unrestraint, ...)
        return settings.calc_raises_properties(properties,
                                               settings.get_context_properties(),
                                               settings.get_context_properties())

    def __call__(self,
                 path: str,
                 index: Optional[int]=None) -> 'TiramisuOption':
        """Select an option by path"""
        subpath = self._option_bag.option.impl_getname() + '.' + path
        subconfig, name = self._subconfig.cfgimpl_get_home_by_path(subpath,
                                                                   self._option_bag.config_bag)
        path = self._option_bag.path + '.' + path
        return TiramisuOption(name,
                              path,
                              index,
                              subconfig,
                              self._option_bag.config_bag)


class _TiramisuOptionOption(_TiramisuOptionOptionDescription):
    """Manage option"""
    def ismulti(self):
        """Test if option could have multi value"""
        option = self._option_bag.option
        return option.impl_is_multi()

    def issubmulti(self):
        """Test if option could have submulti value"""
        option = self._option_bag.option
        return option.impl_is_submulti()

    def isleader(self):
        """Test if option is a leader"""
        option = self._option_bag.option
        return option.impl_is_leader()

    def isfollower(self):
        """Test if option is a follower"""
        option = self._option_bag.option
        return option.impl_is_follower()

    def issymlinkoption(self) -> bool:
        option = self._option_bag.option
        return option.impl_is_symlinkoption()

    def default(self):
        """Get default value for an option (not for optiondescription)"""
        option = self._option_bag.option
        return option.impl_getdefault()

    def defaultmulti(self):
        """Get default value when added a value for a multi option (not for optiondescription)"""
        option = self._option_bag.option
        return option.impl_getdefault_multi()

    def consistencies(self):
        """Get consistencies for an option (not for optiondescription)"""
        option = self._option_bag.option
        return option.get_consistencies()

    def callbacks(self):
        """Get callbacks for an option (not for optiondescription)"""
        option = self._option_bag.option
        return option.impl_get_callback()

    def pattern(self) -> str:
        option = self._option_bag.option
        type = option.get_type()
        if isinstance(option, RegexpOption):
            return option._regexp.pattern
        if type == 'integer':
            # FIXME negative too!
            return r'^[0-9]+$'
        if type == 'domainname':
            return option.impl_get_extra('_domain_re').pattern
        if type in ['ip', 'network', 'netmask']:
            #FIXME only from 0.0.0.0 to 255.255.255.255
            return r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'


class TiramisuOptionOption(CommonTiramisuOption):
    """Manage option"""
    _allow_optiondescription = True
    _follower_need_index = False

    def __new__(cls,
                name,
                subconfig,
                option_bag):
        option = subconfig.cfgimpl_get_description().get_child(name,
                                                               option_bag.config_bag,
                                                               subconfig.cfgimpl_get_path())
        if option.impl_is_optiondescription():
            return _TiramisuOptionOptionDescription(name=name,
                                                    subconfig=subconfig,
                                                    option_bag=option_bag)
        else:
            return _TiramisuOptionOption(name=name,
                                         subconfig=subconfig,
                                         option_bag=option_bag)


class TiramisuOptionOwner(CommonTiramisuOption):
    #FIXME optiondescription must not have Owner!
    """Manage option's owner"""

    def __init__(self,
                 name: str,
                 subconfig: Union[KernelConfig, SubConfig],
                 option_bag: OptionBag) -> None:

        super().__init__(name,
                         subconfig,
                         option_bag)
        if option_bag is not None:
            # for help()
            self._values = self._option_bag.config_bag.context.cfgimpl_get_values()

    def get(self):
        """Get owner for a specified option"""
        option = self._option_bag.option
        return self._values.getowner(self._option_bag)

    def isdefault(self):
        """Is option has defaut value"""
        option = self._option_bag.option
        return self._values.is_default_owner(self._option_bag)

    def set(self, owner):
        """Get owner for a specified option"""
        option = self._option_bag.option
        try:
            obj_owner = getattr(owners, owner)
        except AttributeError:
            owners.addowner(owner)
            obj_owner = getattr(owners, owner)
        self._values.setowner(obj_owner,
                             self._option_bag)


class TiramisuOptionProperty(CommonTiramisuOption):
    """Manage option's property"""
    _allow_optiondescription = True
    _follower_need_index = False

    def __init__(self,
                 name: str,
                 subconfig: Union[KernelConfig, SubConfig],
                 option_bag: OptionBag) -> None:
        super().__init__(name,
                         subconfig,
                         option_bag)
        if option_bag and option_bag.config_bag:
            self._settings = option_bag.config_bag.context.cfgimpl_get_settings()

    def get(self,
            only_raises=False):
        """Get properties for an option"""
        option = self._option_bag.option
        self._test_follower_index()
        properties = self._option_bag.properties
        if not only_raises:
            return properties
        # do not check cache properties/permissives which are not save (unrestraint, ...)
        return self._settings.calc_raises_properties(properties,
                                                     self._settings.get_context_properties(),
                                                     self._settings.get_context_properties())

    def add(self, prop):
        """Add new property for an option"""
        option = self._option_bag.option
        if prop in FORBIDDEN_SET_PROPERTIES:
            raise ConfigError(_('cannot add this property: "{0}"').format(
                ' '.join(prop)))
        props = self._settings.getproperties(self._option_bag,
                                             apply_requires=False)
        self._settings.setproperties(self._option_bag.path,
                                     props | {prop},
                                     self._option_bag,
                                     self._option_bag.config_bag.context)

    def pop(self, prop):
        """Remove new property for an option"""
        option = self._option_bag.option
        props = self._settings.getproperties(self._option_bag,
                                             apply_requires=False)
        self._settings.setproperties(self._option_bag.path,
                                     props - {prop},
                                     self._option_bag,
                                     self._option_bag.config_bag.context)

    def reset(self):
        """Reset all personalised properties"""
        option = self._option_bag.option
        self._settings.reset(self._option_bag,
                             self._option_bag.config_bag.context)


class TiramisuOptionPermissive(CommonTiramisuOption):
    """Manage option's permissive"""
    _allow_optiondescription = True
    _follower_need_index = False

    def __init__(self,
                 name: str,
                 subconfig: Union[KernelConfig, SubConfig],
                 option_bag: OptionBag) -> None:
        super().__init__(name,
                         subconfig,
                         option_bag)
        if option_bag and option_bag.config_bag:
            self._settings = option_bag.config_bag.context.cfgimpl_get_settings()

    def get(self):
        """Get permissives value"""
        return self._settings.getpermissives(self._option_bag.option,
                                             self._option_bag.path)

    def set(self, permissives):
        """Set permissives value"""
        self._settings.setpermissives(self._option_bag,
                                      permissives=permissives)

    def reset(self):
        """Reset all personalised permissive"""
        self._settings.reset_permissives(self._option_bag,
                                         self._option_bag.config_bag.context)


class TiramisuOptionInformation(CommonTiramisuOption):
    """Manage option's informations"""
    _allow_optiondescription = True
    _follower_need_index = False

    def get(self, key, default=undefined):
        """Get information"""
        path = self._option_bag.path
        values = self._option_bag.config_bag.context.cfgimpl_get_values()
        try:
            return values.get_information(key, default, path=path)
        except ValueError:
            option = self._option_bag.option
            return option.impl_get_information(key, default)

    def set(self, key, value):
        """Set information"""
        path = self._option_bag.path
        values = self._option_bag.config_bag.context.cfgimpl_get_values()
        values.set_information(key, value, path=path)

    def reset(self,
              key):
        """Remove information"""
        path = self._option_bag.path
        values = self._option_bag.config_bag.context.cfgimpl_get_values()
        values.del_information(key, path=path)

    def list(self):
        """List information's keys"""
        path = self._option_bag.path
        values = self._option_bag.config_bag.context.cfgimpl_get_values()
        return values.list_information(path)


class _TiramisuOptionValueOption:
    def get(self):
        """Get option's value"""
        option = self._option_bag.option
        self._test_follower_index()
        return self._subconfig.getattr(self._name,
                                       self._option_bag)

    def set(self, value):
        """Change option's value"""
        option = self._option_bag.option
        self._test_follower_index()
        values = self._option_bag.config_bag.context.cfgimpl_get_values()
        if isinstance(value, list):
            while undefined in value:
                idx = value.index(undefined)
                soption_bag = self._option_bag.copy()
                soption_bag.index = idx
                value[idx] = values.getdefaultvalue(soption_bag)
        elif value == undefined:
            value = values.getdefaultvalue(self._option_bag)
        self._subconfig.setattr(value,
                               self._option_bag)

    def reset(self):
        """Reset value for an option"""
        self._test_follower_index()
        self._subconfig.delattr(self._option_bag)

    def default(self):
        """Get default value (default of option or calculated value)"""
        option = self._option_bag.option
        values = self._option_bag.config_bag.context.cfgimpl_get_values()
        if option.impl_is_follower() and self._option_bag.index is None:
            value = []
            length = self._subconfig.cfgimpl_get_length_leadership(self._option_bag)
            for idx in range(length):
                soption_bag = OptionBag()
                soption_bag.set_option(option,
                                       self._option_bag.path,
                                       idx,
                                       self._option_bag.config_bag)
                value.append(values.getdefaultvalue(soption_bag))
            return value
        else:
            return values.getdefaultvalue(self._option_bag)


class _TiramisuOptionValueLeader:
    def pop(self, index):
        """Pop a value"""
        option_bag = self._option_bag
        assert not option_bag.option.impl_is_symlinkoption(), _("can't delete a SymLinkOption")
        option_bag.config_bag.context.cfgimpl_get_values().reset_leadership(index,
                                                                            option_bag,
                                                                            self._subconfig)

    def len(self):
        """Length of leadership"""
        option = self._option_bag.option
        # for example if index is None
        if '_length' not in vars(self):
            self._length = self._subconfig.cfgimpl_get_length()
        return self._length


class _TiramisuOptionValueGroup:
    def reset(self):
        """Reset value"""
        self._option_bag.config_bag.context.reset(self._option_bag.path)


class _TiramisuOptionValueFollower:
    def len(self):
        """Length of follower option"""
        option = self._option_bag.option
        # for example if index is None
        if '_length' not in vars(self):
            self._length = self._subconfig.cfgimpl_get_length_leadership(self._option_bag)
        return self._length


class _TiramisuOptionValueChoiceOption:
    def list(self):
        """All values available for a ChoiceOption"""
        option = self._option_bag.option
        return option.impl_get_values(self._option_bag)


class _TiramisuOptionValueOptionDescription:
    def dict(self,
             flatten=False,
             withvalue=undefined,
             withoption=None,
             withwarning: bool=False,
             fullpath=False):
        """Dict with path as key and value"""
        self._get_option()
        name = self._option_bag.option.impl_getname()
        subconfig = self._subconfig.get_subconfig(self._option_bag)
        config_bag = self._option_bag.config_bag
        if not withwarning and config_bag.properties and 'warnings' in config_bag.properties:
            config_bag = config_bag.copy()
            config_bag.remove_warnings()
        return subconfig.make_dict(config_bag=config_bag,
                                   flatten=flatten,
                                   fullpath=fullpath,
                                   withoption=withoption,
                                   withvalue=withvalue)


class TiramisuOptionValue(CommonTiramisuOption):
    """Manage option's value"""
    _allow_optiondescription = True
    _follower_need_index = False

    def __new__(cls,
                name,
                subconfig,
                option_bag):
        if subconfig is not None:
            option = subconfig.cfgimpl_get_description().get_child(name,
                                                                   option_bag.config_bag,
                                                                   subconfig.cfgimpl_get_path())
        else:
            option = None
        types = [CommonTiramisuOption]
        if option:
            if option.impl_is_optiondescription():
                types.append(_TiramisuOptionValueOptionDescription)
            else:
                types.append(_TiramisuOptionValueOption)
                if isinstance(option, ChoiceOption):
                    types.append(_TiramisuOptionValueChoiceOption)
                if option.impl_is_leader():
                    types.append(_TiramisuOptionValueLeader)
                elif option.impl_is_follower():
                    types.append(_TiramisuOptionValueFollower)
        if option_bag.config_bag.context.impl_type == 'group':
            types.append(_TiramisuOptionValueGroup)
        new_type_dict = {'_allow_optiondescription': cls._allow_optiondescription,
                         '_follower_need_index': cls._follower_need_index}
        new_type = type('TiramisuOptionValue', tuple(types), new_type_dict)(name=name,
                                                                            subconfig=subconfig,
                                                                            option_bag=option_bag)
        new_type.__doc__ = cls.__doc__
        return new_type


def _registers(_registers: Dict[str, type],
               prefix: str,
               extra_type: Optional[type]=None) -> None:
    for module_name in globals().keys():
        if module_name != prefix and module_name.startswith(prefix):
            module = globals()[module_name]
            func_name = module_name[len(prefix):].lower()
            _registers[func_name] = module


class _TiramisuOption(CommonTiramisu):
    """Manage selected option"""
    _registers = {}
    def __init__(self,
                 name: Optional[str],
                 path: Optional[str]=None,
                 index: Optional[int]=None,
                 subconfig: Union[None, KernelConfig, SubConfig]=None,
                 config_bag: Optional[ConfigBag]=None) -> None:
        self._name = name
        self._subconfig = subconfig
        self._path = path
        self._index = index
        self._config_bag = config_bag
        self._option_bag = OptionBag()
        self._option_bag.path = self._path
        self._option_bag.index = self._index
        self._option_bag.config_bag = self._config_bag
        self._tiramisu_dict = None
        if not self._registers:
            _registers(self._registers, 'TiramisuOption')

    def __getattr__(self, subfunc: str) -> Any:
        if subfunc in self._registers:
            return self._registers[subfunc](self._name,
                                            self._subconfig,
                                            self._option_bag)
        raise APIError(_('please specify a valid sub function ({})').format(subfunc))  # pragma: no cover


class _TiramisuOptionDescription(_TiramisuOption):
    def find(self,
             name: str,
             value=undefined,
             type=None,
             first: bool=False):
        """find an option by name (only for optiondescription)"""
        if not first:
            ret = []
        option = self._get_option()
        oname = option.impl_getname()
        path = self._subconfig._get_subpath(oname)
        option_bag = OptionBag()
        option_bag.set_option(option,
                              path,
                              None,
                              self._config_bag)
        subconfig = self._subconfig.get_subconfig(option_bag)
        for path in subconfig.find(byname=name,
                                   byvalue=value,
                                   bytype=type,
                                   _subpath=self._path,
                                   config_bag=self._config_bag):
            subconfig, name = self._config_bag.context.cfgimpl_get_home_by_path(path,
                                                                               self._config_bag)
            t_option = TiramisuOption(name,
                                      path,
                                      None,  # index for a follower ?
                                      subconfig,
                                      self._config_bag)
            if first:
                return t_option
            ret.append(t_option)
        return ret

    def group_type(self):
        """Get type for an optiondescription (only for optiondescription)"""
        return self._get_option().impl_get_group_type()

    def _filter(self,
                opt,
                subconfig):
        if self._config_bag.properties:
            name = opt.impl_getname()
            path = subconfig._get_subpath(name)
            option_bag = OptionBag()
            option_bag.set_option(opt,
                                  path,
                                  None,
                                  self._config_bag)
            if opt.impl_is_optiondescription():
                self._subconfig.get_subconfig(option_bag)
            else:
                subconfig.getattr(name,
                                  option_bag)

    def list(self,
             type='option',
             group_type=None):
        """List options in an optiondescription (only for optiondescription)"""
        assert type in ('all', 'option', 'optiondescription'), _('unknown list type {}').format(type)
        assert group_type is None or isinstance(group_type, groups.GroupType), \
                _("unknown group_type: {0}").format(group_type)
        option = self._get_option()
        name = option.impl_getname()
        path = self._subconfig._get_subpath(name)
        option_bag = OptionBag()
        option_bag.set_option(option,
                              path,
                              None,
                              self._config_bag)
        subconfig = self._subconfig.get_subconfig(option_bag)
        for opt in option.get_children(self._config_bag):
            try:
                self._filter(opt,
                             subconfig)
            except PropertiesOptionError:
                continue
            if opt.impl_is_optiondescription():
                if type == 'option' or (type == 'optiondescription' and group_type and \
                        opt.impl_get_group_type() != group_type):
                    continue
            elif type == 'optiondescription':
                continue
            name = opt.impl_getname()
            yield TiramisuOption(name,
                                 subconfig._get_subpath(name),
                                 None,
                                 subconfig,
                                 self._config_bag)

    def dict(self,
             clearable: str="all",
             remotable: str="minimum",
             form: List=[]) -> Dict:
        """convert config and option to tiramisu format"""
        if self._tiramisu_dict is None:
            option = self._get_option()
            name = option.impl_getname()
            root = self._subconfig._get_subpath(name)
            config = self._config_bag.context
            self._tiramisu_dict = TiramisuDict(Config(self._config_bag.context),
                                               root=root,
                                               clearable=clearable,
                                               remotable=remotable)
        return self._tiramisu_dict.todict(form)

    def updates(self,
                body: List) -> Dict:
        """updates value with tiramisu format"""
        if self._tiramisu_dict is None:
            raise APIError(_('please use .dict() before .updates()'))
        return self._tiramisu_dict.set_updates(body)


class TiramisuOption(CommonTiramisuOption):
    """Manage selected option"""
    def __new__(cls,
                name: Optional[str],
                path: Optional[str]=None,
                index: Optional[int]=None,
                subconfig: Union[None, KernelConfig, SubConfig]=None,
                config_bag: Optional[ConfigBag]=None) -> None:
        if subconfig:
            option = subconfig.cfgimpl_get_description().get_child(name,
                                                                   config_bag,
                                                                   subconfig.cfgimpl_get_path())
            if option.impl_is_optiondescription():
                return _TiramisuOptionDescription(name=name,
                                                  path=path,
                                                  index=index,
                                                  subconfig=subconfig,
                                                  config_bag=config_bag)
        return _TiramisuOption(name=name,
                               path=path,
                               index=index,
                               subconfig=subconfig,
                               config_bag=config_bag)


#__________________________________________________________________________________________________
#


class TiramisuContext(TiramisuHelp):
    def __init__(self,
            config_bag: Optional[ConfigBag]) -> None:
        self._config_bag = config_bag

    def _return_config(self,
                       config):
        if isinstance(config, KernelConfig):
            return Config(config)
        if isinstance(config, KernelMetaConfig):
            return MetaConfig(config)
        if isinstance(config, KernelMixConfig):
            return MixConfig([], config)
        if isinstance(config, KernelGroupConfig):
            return GroupConfig(config)
        raise Exception(_('unknown config type {}').format(type(config)))


class TiramisuContextInformation(TiramisuContext):
    """Manage config informations"""
    def get(self, name, default=undefined):
        """Get an information"""
        return self._config_bag.context.impl_get_information(name, default)

    def set(self, name, value):
        """Set an information"""
        self._config_bag.context.impl_set_information(name, value)

    def reset(self, name):
        """Remove an information"""
        self._config_bag.context.impl_del_information(name)

    def list(self):
        """List information's keys"""
        return self._config_bag.context.impl_list_information()


class TiramisuContextValue(TiramisuContext):
    """Manage config value"""
    def mandatory(self):
        """Return path of options with mandatory property without any value"""
        return self._config_bag.context.cfgimpl_get_values().mandatory_warnings(self._config_bag)

    def set(self,
            path: str,
            value,
            index=None,
            only_config=undefined,
            force_default=undefined,
            force_default_if_same=undefined,
            force_dont_change_value=undefined):
        """Set a value in config or children for a path"""
        kwargs = {}
        if only_config is not undefined:
            kwargs['only_config'] = only_config
        if force_default is not undefined:
            kwargs['force_default'] = force_default
        if force_default_if_same is not undefined:
            kwargs['force_default_if_same'] = force_default_if_same
        if force_dont_change_value is not undefined:
            kwargs['force_dont_change_value'] = force_dont_change_value
        return self._config_bag.context.set_value(path,
                                                  index,
                                                  value,
                                                  self._config_bag,
                                                  **kwargs)

    def reset(self,
              path: str,
              only_children: bool=False):
        """Reset value"""
        self._config_bag.context.reset(path,
                                       only_children,
                                       self._config_bag)

    def dict(self,
             flatten=False,
             withvalue=undefined,
             withoption=None,
             withwarning: bool=False,
             fullpath=False):
        """Dict with path as key and value"""
        config_bag = self._config_bag
        if not withwarning and config_bag.properties and 'warnings' in config_bag.properties:
            config_bag = config_bag.copy()
            config_bag.remove_warnings()
        return config_bag.context.make_dict(config_bag,
                                            flatten=flatten,
                                            fullpath=fullpath,
                                            withoption=withoption,
                                            withvalue=withvalue)

    def exportation(self,
                    with_default_owner: bool=False):
        """Export all values"""
        exportation = self._config_bag.context.cfgimpl_get_values()._p_.exportation()
        if not with_default_owner:
            exportation = [list(exportation[0]), list(exportation[1]), list(exportation[2]), list(exportation[3])]
            index = exportation[0].index(None)
            exportation[0].pop(index)
            exportation[1].pop(index)
            exportation[2].pop(index)
            exportation[3].pop(index)
        return exportation

    def importation(self, values):
        """Import values"""
        if None not in values[0]:
            context_owner = self._config_bag.context.cfgimpl_get_values().get_context_owner()
        else:
            context_owner = None
        self._config_bag.context.cfgimpl_get_values()._p_.importation(values)
        self._config_bag.context.cfgimpl_reset_cache(None, None)
        if context_owner is not None:
            self._config_bag.context.cfgimpl_get_values()._p_.setvalue(None,
                                                                      None,
                                                                      context_owner,
                                                                      None,
                                                                      True)


class TiramisuContextOwner(TiramisuContext):
    """Global owner"""

    def get(self):
        """Get owner"""
        return self._config_bag.context.cfgimpl_get_values().get_context_owner()

    def set(self, owner):
        """Set owner"""
        try:
            obj_owner = getattr(owners, owner)
        except AttributeError:
            owners.addowner(owner)
            obj_owner = getattr(owners, owner)
        self._config_bag.context.cfgimpl_get_values().set_context_owner(obj_owner)


class TiramisuContextProperty(TiramisuContext):
    """Manage config properties"""

    def read_only(self):
        """Set config to read only mode"""
        old_props = self._config_bag.properties
        settings = self._config_bag.context.cfgimpl_get_settings()
        settings.read_only(self._config_bag.context)
        del self._config_bag.properties
        if 'force_store_value' not in old_props and \
                'force_store_value' in self._config_bag.properties:
            self._force_store_value()

    def read_write(self):
        """Set config to read and write mode"""
        old_props = self._config_bag.properties
        settings = self._config_bag.context.cfgimpl_get_settings()
        settings.read_write(self._config_bag.context)
        or_properties = settings.rw_append - settings.ro_append - SPECIAL_PROPERTIES
        permissives = frozenset(settings.get_context_permissives() | or_properties)
        settings.set_context_permissives(permissives)
        del self._config_bag.properties
        if 'force_store_value' not in old_props and \
                'force_store_value' in self._config_bag.properties:
            self._force_store_value()

    def add(self, prop):
        """Add a config property"""
        props = set(self.get())
        props.add(prop)
        self.set(frozenset(props))

    def pop(self, prop):
        """Remove a config property"""
        props = set(self.get())
        if prop in props:
            props.remove(prop)
            self.set(frozenset(props))

    def get(self):
        """Get all config properties"""
        return self._config_bag.properties

    def set(self, props):
        """Personalise config properties"""
        if 'force_store_value' in props:
            force_store_value = 'force_store_value' not in self._config_bag.properties
        else:
            force_store_value = False
        context = self._config_bag.context
        context.cfgimpl_get_settings().set_context_properties(props,
                                                              context)
        del self._config_bag.properties
        if force_store_value:
            self._force_store_value()

    def reset(self):
        """Remove config properties"""
        context = self._config_bag.context
        context.cfgimpl_get_settings().reset(None,
                                             context)
        del self._config_bag.properties

    def exportation(self):
        """Export config properties"""
        return self._config_bag.context.cfgimpl_get_settings()._p_.exportation()

    def importation(self, properties):
        """Import config properties"""
        if 'force_store_value' in properties.get(None, []):
            force_store_value = 'force_store_value' not in self._config_bag.properties
        else:
            force_store_value = False
        self._config_bag.context.cfgimpl_get_settings()._p_.importation(properties)
        self._config_bag.context.cfgimpl_reset_cache(None, None)
        del self._config_bag.properties
        if force_store_value:
            self._force_store_value()

    def _force_store_value(self):
        descr = self._config_bag.context.cfgimpl_get_description()
        descr.impl_build_force_store_values(self._config_bag)

    def setdefault(self,
                   properties: Set[str],
                   type: Optional[str]=None,
                   when: Optional[str]=None) -> None:
        if not isinstance(properties, set):
            raise TypeError(_('properties must be a set'))
        setting = self._config_bag.context.cfgimpl_get_settings()
        if type is None and when is None:
            setting.default_properties = properties
        else:
            if when not in ['append', 'remove']:
                raise ValueError(_('unknown when {} (must be in append or remove)').format(when))
            if type == 'read_only':
                if when == 'append':
                    setting.ro_append = properties
                else:
                    setting.ro_remove = properties
            elif type == 'read_write':
                if when == 'append':
                    setting.rw_append = properties
                else:
                    setting.rw_remove = properties
            else:
                raise ValueError(_('unknown type {}').format(type))

    def getdefault(self,
                   type: Optional[str]=None,
                   when: Optional[str]=None) -> Set[str]:
        setting = self._config_bag.context.cfgimpl_get_settings()
        if type is None and when is None:
            return setting.default_properties

        if when not in ['append', 'remove']:
            raise ValueError(_('unknown when {} (must be in append or remove)').format(when))
        if type == 'read_only':
            if when == 'append':
                return setting.ro_append
            else:
                return setting.ro_remove
        elif type == 'read_write':
            if when == 'append':
                return setting.rw_append
            else:
                return setting.rw_remove
        else:
            raise ValueError(_('unknown type {}').format(type))


class TiramisuContextPermissive(TiramisuContext):
    """Manage config permissives"""

    def get(self):
        """Get config permissives"""
        return self._config_bag.context.cfgimpl_get_settings().get_context_permissives()

    def set(self, permissives):
        """Set config permissives"""
        self._config_bag.context.cfgimpl_get_settings().set_context_permissives(permissives)
        del self._config_bag.permissives

    def exportation(self):
        """Export config permissives"""
        return self._config_bag.context.cfgimpl_get_settings()._pp_.exportation()

    def importation(self, permissives):
        """Import config permissives"""
        self._config_bag.context.cfgimpl_get_settings()._pp_.importation(permissives)
        self._config_bag.context.cfgimpl_reset_cache(None,
                                                     None)
        del self._config_bag.permissives

    def reset(self):
        """Remove config permissives"""
        context = self._config_bag.context
        context.cfgimpl_get_settings().reset_permissives(None,
                                                         context)
        del self._config_bag.properties

    def add(self, prop):
        """Add a config permissive"""
        props = set(self.get())
        props.add(prop)
        self.set(frozenset(props))

    def pop(self, prop):
        """Remove a config permissive"""
        props = set(self.get())
        if prop in props:
            props.remove(prop)
            self.set(frozenset(props))


class TiramisuContextOption(TiramisuContext):
    def __init__(self,
                 *args,
                 **kwargs) -> None:
        self._tiramisu_dict = None
        super().__init__(*args, **kwargs)

    def _find(self,
              name,
              value,
              type):
        for path in self._config_bag.context.find(byname=name,
                                                  byvalue=value,
                                                  bytype=type,
                                                  config_bag=self._config_bag):
            subconfig, name = self._config_bag.context.cfgimpl_get_home_by_path(path,
                                                                                self._config_bag)
            yield TiramisuOption(name,
                                 path,
                                 None,
                                 subconfig,
                                 self._config_bag)

    def find(self,
             name,
             value=undefined,
             type=None,
             first=False):
        """Find an or a list of options"""
        if first:
            return next(self._find(name, value, type))
        return self._find(name, value, type)

    def _filter(self,
                opt,
                subconfig,
                config_bag):
        option_bag = OptionBag()
        option_bag.set_option(opt,
                              opt.impl_getpath(),
                              None,
                              config_bag)
        if opt.impl_is_optiondescription():
            config_bag.context.cfgimpl_get_settings().validate_properties(option_bag)
            return subconfig.get_subconfig(option_bag)
        subconfig.getattr(opt.impl_getname(),
                          option_bag)

    def _walk(self,
              option,
              recursive,
              type_,
              group_type,
              config_bag,
              subconfig):
        for opt in option.get_children(config_bag):
            try:
                subsubconfig = self._filter(opt,
                                            subconfig,
                                            config_bag)
            except PropertiesOptionError:
                continue
            if opt.impl_is_optiondescription():
                if recursive:
                    for toption in self._walk(opt,
                                              recursive,
                                              type_,
                                              group_type,
                                              config_bag,
                                              subsubconfig):
                        yield toption
                if type_ == 'option' or (type_ == 'optiondescription' and \
                        group_type and opt.impl_get_group_type() != group_type):
                    continue
            elif type_ == 'optiondescription':
                continue
            name = opt.impl_getname()
            path = opt.impl_getpath()
            yield TiramisuOption(name,
                                 path,
                                 None,
                                 subconfig,
                                 self._config_bag)

    def list(self,
             type='option',
             group_type=None,
             recursive=False):
        """List options (by default list only option)"""
        assert type in ('all', 'option', 'optiondescription'), _('unknown list type {}').format(type)
        assert group_type is None or isinstance(group_type, groups.GroupType), \
                _("unknown group_type: {0}").format(group_type)
        config_bag = self._config_bag
        if config_bag.properties and 'warnings' in config_bag.properties:
            config_bag = config_bag.copy()
            config_bag.remove_warnings()
        option = config_bag.context.cfgimpl_get_description()
        for toption in self._walk(option,
                                  recursive,
                                  type,
                                  group_type,
                                  config_bag,
                                  config_bag.context):
            yield toption

    def dict(self,
             clearable="all",
             remotable="minimum",
             form=[]):
        """convert config and option to tiramisu format"""
        if self._tiramisu_dict is None:
            self._tiramisu_dict = TiramisuDict(Config(self._config_bag.context),
                                               root=None,
                                               clearable=clearable,
                                               remotable=remotable)
        return self._tiramisu_dict.todict(form)

    def updates(self,
                body: List) -> Dict:
        """updates value with tiramisu format"""
        if self._tiramisu_dict is None:
            raise APIError(_('please use .dict() before .updates()'))
        return self._tiramisu_dict.set_updates(body)


class _TiramisuContextConfigReset():
    def reset(self):
        """Remove all datas to current config (informations, values, properties, ...)"""
        # Option's values
        context_owner = self._config_bag.context.cfgimpl_get_values().get_context_owner()
        self._config_bag.context.cfgimpl_get_values()._p_.importation((tuple(), tuple(), tuple(), tuple()))
        self._config_bag.context.cfgimpl_get_values()._p_.setvalue(None,
                                                                  None,
                                                                  context_owner,
                                                                  None,
                                                                  True)
        # Option's informations
        self._config_bag.context.cfgimpl_get_values()._p_.del_informations()
        # Option's properties
        self._config_bag.context.cfgimpl_get_settings()._p_.importation({})
        # Option's permissives
        self._config_bag.context.cfgimpl_get_settings()._pp_.importation({})
        # Remove cache
        self._config_bag.context.cfgimpl_reset_cache(None, None)


class _TiramisuContextConfig(TiramisuContext, _TiramisuContextConfigReset):
    """Actions to Config"""
    def name(self):
        return self._config_bag.context.impl_getname()

    def copy(self,
             session_id=None,
             persistent=False,
             storage=None):
        return self._return_config(self._config_bag.context.duplicate(session_id,
                                                                      persistent=persistent,
                                                                      storage=storage))

    def deepcopy(self,
                  session_id=None,
                  persistent=False,
                  storage=None,
                  metaconfig_prefix=None):
        return self._return_config(self._config_bag.context.duplicate(session_id,
                                                                      persistent=persistent,
                                                                      storage=storage,
                                                                      metaconfig_prefix=metaconfig_prefix,
                                                                      deep=True))

    def metaconfig(self):
        return self._return_config(self._config_bag.context.cfgimpl_get_meta())

    def path(self):
        return self._config_bag.context.cfgimpl_get_config_path()


class _TiramisuContextGroupConfig(TiramisuContext):
    """Actions to GroupConfig"""
    def name(self):
        """Get config name"""
        return self._config_bag.context.impl_getname()

    def list(self):
        """List children's config"""
        for child in self._config_bag.context.cfgimpl_get_children():
            yield self._return_config(child)

    def find(self,
             name: str,
             value=undefined):
        """Find an or a list of config with finding option"""
        return GroupConfig(self._config_bag.context.find_group(byname=name,
                                                               byvalue=value,
                                                               config_bag=self._config_bag))

    def __call__(self,
                 path: Optional[str]):
        """select a child Tiramisu config"""
        if path is None:
            return self._return_config(self._config_bag.context)
        spaths = path.split('.')
        config = self._config_bag.context
        for spath in spaths:
            config = config.getconfig(spath)
        return self._return_config(config)

    def copy(self,
             session_id=None,
             persistent=False,
             storage=None):
        return self._return_config(self._config_bag.context.duplicate(session_id,
                                                                      persistent=persistent,
                                                                      storage=storage))

    def deepcopy(self,
                  session_id=None,
                  persistent=False,
                  storage=None,
                  metaconfig_prefix=None):
        return self._return_config(self._config_bag.context.duplicate(session_id,
                                                                      persistent=persistent,
                                                                      storage=storage,
                                                                      metaconfig_prefix=metaconfig_prefix,
                                                                      deep=True))

    def path(self):
        return self._config_bag.context.cfgimpl_get_config_path()

    def get(self,
            name: str) -> 'Config':
        return self._return_config(self._config_bag.context.getconfig(name))


class _TiramisuContextMixConfig(_TiramisuContextGroupConfig, _TiramisuContextConfigReset):
    """Actions to MixConfig"""
    def pop(self,
            session_id):
        """Remove config from MetaConfig"""
        return self._return_config(self._config_bag.context.pop_config(session_id=session_id))

    def add(self,
            config):
        """Add config from MetaConfig"""
        self._config_bag.context.add_config(config)


class _TiramisuContextMetaConfig(_TiramisuContextMixConfig):
    """Actions to MetaConfig"""
    def new(self,
            session_id,
            persistent=False,
            type='config'):
        """Create and add a new config"""
        new_config = self._config_bag.context.new_config(session_id=session_id,
                                                          persistent=persistent,
                                                          type_=type)
        return self._return_config(new_config)


class TiramisuContextCache(TiramisuContext):
    def reset(self):
        self._config_bag.context.cfgimpl_reset_cache(None, None)

    def set_expiration_time(self,
                            time: int) -> None:
        self._config_bag.expiration_time = time

    def get_expiration_time(self) -> int:
        return self._config_bag.expiration_time


class TiramisuDispatcher:
    pass


class TiramisuAPI(TiramisuHelp):
    _registers = {}

    def __init__(self,
                 config) -> None:
        if not isinstance(config, ConfigBag):
            config = ConfigBag(context=config)
        self._config_bag = config
        if not self._registers:
            _registers(self._registers, 'TiramisuContext')
            _registers(self._registers, 'TiramisuDispatcher')

    def __getattr__(self, subfunc: str) -> Any:
        if subfunc == 'forcepermissive':
            config_bag = self._config_bag.copy()
            config_bag.set_permissive()
            return TiramisuAPI(config_bag)
        elif subfunc == 'unrestraint':
            config_bag = self._config_bag.copy()
            config_bag.unrestraint()
            return TiramisuAPI(config_bag)
        elif subfunc == 'config':
            config_type = self._config_bag.context.impl_type
            if config_type == 'group':
                config = _TiramisuContextGroupConfig
            elif config_type == 'meta':
                config = _TiramisuContextMetaConfig
            elif config_type == 'mix':
                config = _TiramisuContextMixConfig
            else:
                config = _TiramisuContextConfig
            return config(self._config_bag)
        elif subfunc in self._registers:
            config_bag = self._config_bag
            del config_bag.permissives
            return self._registers[subfunc](config_bag)
        raise APIError(_('please specify a valid sub function ({})').format(subfunc))

    def __dir__(self):
        return list(self._registers.keys()) + ['unrestraint', 'forcepermissive', 'config']


class TiramisuDispatcherOption(TiramisuDispatcher, TiramisuContextOption):
    """Select an option"""
    def __call__(self,
                 path: str,
                 index: Optional[int]=None) -> TiramisuOption:
        """Select an option by path"""
        if self._config_bag.context.impl_type == 'group':
            subpath, name = path.rsplit('.', 1)
            subconfig = None
        else:
            subconfig, name = self._config_bag.context.cfgimpl_get_home_by_path(path,
                                                                                self._config_bag)
        return TiramisuOption(name,
                              path,
                              index,
                              subconfig,
                              self._config_bag)


#__________________________________________________________________________________________________
class Config(TiramisuAPI):
    """Root config object that enables us to handle the configuration options"""
    def __init__(self,
                 descr: OptionDescription,
                 session_id: str=None,
                 persistent: bool=False,
                 storage=None) -> None:
        if isinstance(descr, KernelConfig):
            config = descr
        else:
            config = KernelConfig(descr,
                                  session_id=session_id,
                                  persistent=persistent,
                                  storage=storage)
        super().__init__(config)


class MetaConfig(TiramisuAPI):
    """MetaConfig object that enables us to handle the sub configuration's options"""
    def __init__(self,
                 children,
                 session_id: Union[str, None]=None,
                 persistent: bool=False,
                 optiondescription: Optional[OptionDescription]=None) -> None:
        if isinstance(children, KernelMetaConfig):
            config = children
        else:
            _children = []
            for child in children:
                if isinstance(child, TiramisuAPI):
                    _children.append(child._config_bag.context)
                else:
                    _children.append(child)

            config = KernelMetaConfig(_children,
                                      session_id=session_id,
                                      persistent=persistent,
                                      optiondescription=optiondescription)
        super().__init__(config)


class MixConfig(TiramisuAPI):
    """MetaConfig object that enables us to handle the sub configuration's options"""
    def __init__(self,
                 optiondescription: OptionDescription,
                 children: List[Config],
                 session_id: Optional[str]=None,
                 persistent: bool=False) -> None:
        if isinstance(children, KernelMixConfig):
            config = children
        else:
            _children = []
            for child in children:
                if isinstance(child, TiramisuAPI):
                    _children.append(child._config_bag.context)
                else:
                    _children.append(child)

            config = KernelMixConfig(optiondescription,
                                      _children,
                                      session_id=session_id,
                                      persistent=persistent)
        super().__init__(config)


class GroupConfig(TiramisuAPI):
    """GroupConfig that enables us to access the Config"""
    def __init__(self,
                 children,
                 session_id: Optional[str]=None) -> None:
        if isinstance(children, KernelGroupConfig):
            config = children
        else:
            _children = []
            for child in children:
                if isinstance(child, TiramisuAPI):
                    _children.append(child._config_bag.context)
                else:
                    _children.append(child)

            config = KernelGroupConfig(_children,
                                       session_id=session_id)
        super().__init__(config)
