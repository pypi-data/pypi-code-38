# -*- coding: utf-8 -*-
"takes care of the option's values and multi values"
# Copyright (C) 2013-2019 Team tiramisu (see AUTHORS for all contributors)
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
import weakref
from typing import Optional, Any, Callable
from .error import ConfigError, PropertiesOptionError, RequirementError
from .setting import owners, undefined, forbidden_owners, OptionBag, ConfigBag
from .autolib import carry_out_calculation
from .function import Params
from .i18n import _


class Values(object):
    """The `Config`'s root is indeed  in charge of the `Option()`'s values,
    but the values are physicaly located here, in `Values`, wich is also
    responsible of a caching utility.
    """
    __slots__ = ('_p_',
                 '__weakref__')

    def __init__(self,
                 storage):
        """
        Initializes the values's dict.

        :param storage: where values or owners are stored

        """
        # store the storage
        self._p_ = storage
        # set default owner
        if self._p_.getowner(None, None) is None:
            self._p_.setvalue(None,
                              None,
                              owners.user,
                              None,
                              True)

    #______________________________________________________________________
    # get value

    def get_cached_value(self,
                         option_bag):
        """get value directly in cache if set
        otherwise calculated value and set it in cache

        :returns: value
        """
        # try to retrive value in cache
        setting_properties = option_bag.config_bag.properties
        is_cached, value = self._p_.getcache(option_bag.path,
                                             option_bag.config_bag.expiration_time,
                                             option_bag.index,
                                             setting_properties,
                                             option_bag.properties,
                                             'value')

        if not is_cached:
            # no cached value so get value
            value = self.getvalue(option_bag)
        # validate value
        opt = option_bag.option
        opt.impl_validate(value,
                          option_bag,
                          check_error=True)
        if 'warnings' in setting_properties:
            opt.impl_validate(value,
                              option_bag,
                              check_error=False)
        # store value in cache
        if not is_cached:
            self._p_.setcache(option_bag.path,
                              option_bag.index,
                              value,
                              option_bag.properties,
                              setting_properties)
        if isinstance(value, list):
            # return a copy, so value cannot be modified
            return value.copy()
        # and return it
        return value

    def force_to_metaconfig(self, option_bag):
        # force_metaconfig_on_freeze in config => to metaconfig
        # force_metaconfig_on_freeze in option + config is kernelconfig => to metaconfig
        settings = option_bag.config_bag.context.cfgimpl_get_settings()
        if 'force_metaconfig_on_freeze' in option_bag.properties:
            settings = option_bag.config_bag.context.cfgimpl_get_settings()
            if 'force_metaconfig_on_freeze' in option_bag.option.impl_getproperties() and \
                    not settings._p_.getproperties(option_bag.path, frozenset()):
                # if force_metaconfig_on_freeze is only in option (not in config)
                return option_bag.config_bag.context.impl_type == 'config'
            else:
                return True
        return False

    def getvalue(self,
                 option_bag):
        """actually retrieves the value

        :param path: the path of the `Option`
        :param index: index for a follower `Option`

        :returns: value
        """
        # get owner and value from store
        # index allowed only for follower
        index = option_bag.index
        is_follower = option_bag.option.impl_is_follower()
        if index is None or not is_follower:
            _index = None
        else:
            _index = index
        owner, value = self._p_.getowner(option_bag.path,
                                         owners.default,
                                         index=_index,
                                         with_value=True)
        if owner != owners.default and \
                not ('frozen' in option_bag.properties and 'force_default_on_freeze' in option_bag.properties) and \
                not ('frozen' in option_bag.properties and self.force_to_metaconfig(option_bag)):
            return value
        return self.getdefaultvalue(option_bag)

    def getdefaultvalue(self,
                        option_bag):
        """get default value:
        - get meta config value or
        - get calculated value or
        - get default value
        """
        moption_bag = self._get_meta(option_bag)
        if moption_bag:
            # retrieved value from meta config
            return moption_bag.config_bag.context.cfgimpl_get_values().get_cached_value(moption_bag)

        if option_bag.option.impl_has_callback():
            # default value is a calculated value
            value = self.calculate_value(option_bag)
            if value is not undefined:
                return value

        # now try to get default value:
        value = option_bag.option.impl_getdefault()

        # - if option is a submulti, return a list a list
        # - if option is a multi, return a list
        # - default value
        if option_bag.option.impl_is_multi() and option_bag.index is not None:
            # if index, must return good value for this index
            if len(value) > option_bag.index:
                value = value[option_bag.index]
            else:
                # no value for this index, retrieve default multi value
                # default_multi is already a list for submulti
                value = option_bag.option.impl_getdefault_multi()
        return value

    def calculate_value(self,
                        option_bag: OptionBag) -> Any:
        def _reset_cache(_value):
            if not 'expire' in option_bag.properties:
                return
            is_cache, cache_value = self._p_.getcache(option_bag.path,
                                                      None,
                                                      option_bag.index,
                                                      option_bag.config_bag.properties,
                                                      option_bag.properties,
                                                      'value')
            if not is_cache or cache_value == _value:
                # calculation return same value as previous value,
                # so do not invalidate cache
                return
            # calculated value is a new value, so reset cache
            option_bag.config_bag.context.cfgimpl_reset_cache(option_bag)

        # if value has callback, calculate value
        callback, callback_params = option_bag.option.impl_get_callback()
        value = self.carry_out_calculation(option_bag,
                                           callback,
                                           callback_params)
        if isinstance(value, list) and option_bag.index is not None:
            # if value is a list and index is set
            if option_bag.option.impl_is_submulti() and (value == [] or not isinstance(value[0], list)):
                # return value only if it's a submulti and not a list of list
                _reset_cache(value)
                return value
            if len(value) > option_bag.index:
                # return the value for specified index if found
                _reset_cache(value[option_bag.index])
                return value[option_bag.index]
            # there is no calculate value for this index,
            # so return an other default value
        else:
            if option_bag.option.impl_is_submulti():
                if isinstance(value, list):
                    # value is a list, but no index specified
                    if (value != [] and not isinstance(value[0], list)):
                        # if submulti, return a list of value
                        value = [value]
                elif option_bag.index is not None:
                    # if submulti, return a list of value
                    value = [value]
                else:
                    # return a list of list for a submulti
                    value = [[value]]
            elif option_bag.option.impl_is_multi() and not isinstance(value, list) and option_bag.index is None:
                # return a list for a multi
                value = [value]
            _reset_cache(value)
            return value
        return undefined

    def carry_out_calculation(self,
                              option_bag: OptionBag,
                              callback: Callable,
                              callback_params: Optional[Params]) -> Any:
        return carry_out_calculation(option_bag.option,
                                     callback=callback,
                                     callback_params=callback_params,
                                     index=option_bag.index,
                                     config_bag=option_bag.config_bag,
                                     fromconsistency=option_bag.fromconsistency)
    def isempty(self,
                opt,
                value,
                force_allow_empty_list=False,
                index=None):
        "convenience method to know if an option is empty"
        empty = opt._empty
        if index in [None, undefined] and opt.impl_is_multi():
            if force_allow_empty_list:
                allow_empty_list = True
            else:
                allow_empty_list = opt.impl_allow_empty_list()
                if allow_empty_list is undefined:
                    allow_empty_list = opt.impl_is_follower()
            isempty = value is None or (not allow_empty_list and value == []) or \
                None in value or empty in value
        else:
            isempty = value is None or value == empty or (opt.impl_is_submulti() and value == [])
        return isempty

    #______________________________________________________________________
    # set value

    def setvalue(self,
                 value,
                 option_bag,
                 _commit):

        context = option_bag.config_bag.context
        owner = self.get_context_owner()
        if 'validator' in option_bag.config_bag.properties:
            if option_bag.index is not None or option_bag.option.has_consistencies(context):
                # set value to a fake config when option has dependency
                # validation will be complet in this case (consistency, ...)
                tested_context = context._gen_fake_values()
                config_bag = option_bag.config_bag.copy()
                config_bag.remove_validation()
                config_bag.context = tested_context
                soption_bag = option_bag.copy()
                soption_bag.config_bag = config_bag
                tested_context.cfgimpl_get_values().setvalue(value,
                                                             soption_bag,
                                                             True)
                soption_bag.config_bag.properties = option_bag.config_bag.properties
                tested_context.getattr(soption_bag.path,
                                       soption_bag)
            else:
                self.setvalue_validation(value,
                                         option_bag)

        self._setvalue(option_bag,
                       value,
                       owner,
                       commit=_commit)

    def setvalue_validation(self,
                            value,
                            option_bag):

        settings = option_bag.config_bag.context.cfgimpl_get_settings()
        # First validate properties with this value
        opt = option_bag.option
        settings.validate_frozen(option_bag)
        settings.validate_mandatory(value,
                                    option_bag)
        # Value must be valid for option
        opt.impl_validate(value,
                          option_bag,
                          check_error=True)
        if 'warnings' in option_bag.config_bag.properties:
            # No error found so emit warnings
            opt.impl_validate(value,
                              option_bag,
                              check_error=False)

    def _setvalue(self,
                  option_bag,
                  value,
                  owner,
                  commit=True):

        option_bag.config_bag.context.cfgimpl_reset_cache(option_bag)
        if isinstance(value, list):
            # copy
            value = value.copy()
        self._p_.setvalue(option_bag.path,
                          value,
                          owner,
                          option_bag.index,
                          commit)

    def _get_meta(self,
                  option_bag):
        context = option_bag.config_bag.context
        meta = context.cfgimpl_get_meta()
        if meta is None:
            return None
        if option_bag.option.impl_is_follower():
            leader = option_bag.option.impl_get_leadership().get_leader()
            leaderpath = leader.impl_getpath()
            # follower could be a "meta" only if leader hasn't value
            if self._p_.hasvalue(leaderpath,
                                 index=None):
                return None
        doption_bag = option_bag.copy()
        config_bag = option_bag.config_bag.copy()
        config_bag.context = meta
        doption_bag.config_bag = config_bag
        if 'force_metaconfig_on_freeze' in option_bag.properties:
            # remove force_metaconfig_on_freeze only if option in metaconfig
            # hasn't force_metaconfig_on_freeze properties
            ori_properties = doption_bag.properties
            del doption_bag.properties
            if not self.force_to_metaconfig(doption_bag):
                doption_bag.properties = ori_properties - {'force_metaconfig_on_freeze'}
            else:
                doption_bag.properties = ori_properties
        config_bag.unrestraint()
        meta_option_bag = meta.cfgimpl_get_values().getowner(doption_bag,
                                                             only_default=True)
        if meta_option_bag == owners.default:
            return None
        return meta_option_bag


    #______________________________________________________________________
    # owner

    def is_default_owner(self,
                         option_bag,
                         validate_meta=True):
        return self.getowner(option_bag,
                             validate_meta=validate_meta,
                             only_default=True) == owners.default

    def getowner(self,
                 option_bag,
                 validate_meta=True,
                 only_default=False):
        """
        retrieves the option's owner

        :param opt: the `option.Option` object
        :param force_permissive: behaves as if the permissive property
                                 was present
        :returns: a `setting.owners.Owner` object
        """
        context = option_bag.config_bag.context
        opt = option_bag.option
        if opt.impl_is_symlinkoption():
            option_bag.ori_option = opt
            opt = opt.impl_getopt()
            option_bag.option = opt
            option_bag.path = opt.impl_getpath()
        settings = context.cfgimpl_get_settings()
        settings.validate_properties(option_bag)
        if 'frozen' in option_bag.properties and \
                'force_default_on_freeze' in option_bag.properties:
            return owners.default
        if only_default:
            if self._p_.hasvalue(option_bag.path,
                                 option_bag.index):
                owner = option_bag
            else:
                owner = owners.default
        else:
            owner = self._p_.getowner(option_bag.path,
                                      owners.default,
                                      index=option_bag.index)
        if validate_meta is not False and (owner is owners.default or \
                                           'frozen' in option_bag.properties and 'force_metaconfig_on_freeze' in option_bag.properties):
            moption_bag = self._get_meta(option_bag)
            if moption_bag:
                owner = moption_bag.config_bag.context.cfgimpl_get_values().getowner(moption_bag,
                                                                                     only_default=only_default)
            elif 'force_metaconfig_on_freeze' in option_bag.properties:
                return owners.default
        return owner

    def setowner(self,
                 owner,
                 option_bag):
        """
        sets a owner to an option

        :param opt: the `option.Option` object
        :param owner: a valid owner, that is a `setting.owners.Owner` object
        """
        opt = option_bag.option
        if opt.impl_is_symlinkoption():
            raise ConfigError(_("can't set owner for the symlinkoption \"{}\""
                                "").format(opt.impl_get_display_name()))
        if owner in forbidden_owners:
            raise ValueError(_('set owner "{0}" is forbidden').format(str(owner)))

        if not self._p_.hasvalue(option_bag.path):
            raise ConfigError(_('no value for {0} cannot change owner to {1}'
                                '').format(option_bag.path, owner))
        option_bag.config_bag.context.cfgimpl_get_settings().validate_frozen(option_bag)
        self._p_.setowner(option_bag.path,
                          owner,
                          index=option_bag.index)
    #______________________________________________________________________
    # reset

    def reset(self,
              option_bag,
              _commit=True):

        context = option_bag.config_bag.context
        hasvalue = self._p_.hasvalue(option_bag.path)

        if hasvalue and 'validator' in option_bag.config_bag.properties:
            fake_context = context._gen_fake_values()
            config_bag = option_bag.config_bag.copy()
            config_bag.remove_validation()
            config_bag.context = fake_context
            soption_bag = option_bag.copy()
            soption_bag.config_bag = config_bag
            fake_value = fake_context.cfgimpl_get_values()
            fake_value.reset(soption_bag)
            soption_bag.config_bag.properties = option_bag.config_bag.properties
            value = fake_value.getdefaultvalue(soption_bag)
            fake_value.setvalue_validation(value,
                                           soption_bag)
        opt = option_bag.option
        if opt.impl_is_leader():
            opt.impl_get_leadership().reset(self,
                                            option_bag,
                                            _commit=_commit)
        if hasvalue:
            if 'force_store_value' in option_bag.properties:
                value = self.getdefaultvalue(option_bag)

                self._setvalue(option_bag,
                               value,
                               owners.forced,
                               commit=_commit)
            else:
                self._p_.resetvalue(option_bag.path,
                                    _commit)
            context.cfgimpl_reset_cache(option_bag)

    def reset_follower(self,
                       option_bag,
                       _commit=True):

        if self._p_.hasvalue(option_bag.path, index=option_bag.index):
            context = option_bag.config_bag.context
            if 'validator' in option_bag.config_bag.properties:
                fake_context = context._gen_fake_values()
                fake_value = fake_context.cfgimpl_get_values()
                config_bag = option_bag.config_bag.copy()
                config_bag.remove_validation()
                config_bag.context = fake_context
                soption_bag = option_bag.copy()
                soption_bag.config_bag = config_bag
                fake_value.reset_follower(soption_bag)
                value = fake_value.getdefaultvalue(soption_bag)
                fake_value.setvalue_validation(value,
                                               soption_bag)
            self._p_.resetvalue_index(option_bag.path,
                                      option_bag.index,
                                      _commit)
            context.cfgimpl_reset_cache(option_bag)

    def reset_leadership(self,
                         index,
                         option_bag,
                         subconfig):

        current_value = self.get_cached_value(option_bag)
        length = len(current_value)
        if index >= length:
            raise IndexError(_('index "{}" is higher than the length "{}" '
                               'for option "{}"').format(index,
                                                         length,
                                                         option_bag.option.impl_get_display_name()))
        current_value.pop(index)
        self.setvalue(current_value,
                      option_bag,
                      _commit=True)
        subconfig.cfgimpl_get_description().pop(self,
                                                index,
                                                option_bag)

    #______________________________________________________________________
    # information

    def set_information(self, key, value, path=None):
        """updates the information's attribute

        :param key: information's key (ex: "help", "doc"
        :param value: information's value (ex: "the help string")
        """
        self._p_.set_information(path, key, value)

    def get_information(self, key, default=undefined, path=None):
        """retrieves one information's item

        :param key: the item string (ex: "help")
        """
        return self._p_.get_information(path, key, default)

    def del_information(self, key, raises=True, path=None):
        self._p_.del_information(path, key, raises)

    def list_information(self, path=None):
        return self._p_.list_information(path)

    #______________________________________________________________________
    # mandatory warnings
    def _mandatory_warnings(self,
                            context,
                            config_bag,
                            description,
                            currpath,
                            subconfig,
                            od_config_bag):
        settings = context.cfgimpl_get_settings()
        for option in description.get_children(config_bag,
                                               context):
            name = option.impl_getname()
            path = '.'.join(currpath + [name])

            if option.impl_is_optiondescription():
                try:
                    option_bag = OptionBag()
                    option_bag.set_option(option,
                                          path,
                                          None,
                                          od_config_bag)
                    subsubconfig = subconfig.get_subconfig(option_bag)
                except PropertiesOptionError as err:
                    pass
                else:
                    for path in self._mandatory_warnings(context,
                                                         config_bag,
                                                         option,
                                                         currpath + [name],
                                                         subsubconfig,
                                                         od_config_bag):
                        yield path
            elif not option.impl_is_symlinkoption():
                # don't verifying symlink
                try:
                    if not option.impl_is_follower():
                        option_bag = OptionBag()
                        option_bag.set_option(option,
                                              path,
                                              None,
                                              config_bag)
                        if 'mandatory' in option_bag.properties or 'empty' in option_bag.properties:
                            subconfig.getattr(name,
                                              option_bag)
                    else:
                        for index in range(subconfig.cfgimpl_get_length()):
                            option_bag = OptionBag()
                            option_bag.set_option(option,
                                                  path,
                                                  index,
                                                  config_bag)
                            if 'mandatory' in option_bag.properties:
                                subconfig.getattr(name,
                                                  option_bag)
                except PropertiesOptionError as err:
                    if err.proptype == ['mandatory']:
                        yield path
                except RequirementError:
                    pass
                except ConfigError as err:
                    #assume that uncalculated value is an empty value
                    yield path

    def mandatory_warnings(self,
                           config_bag):
        """convenience function to trace Options that are mandatory and
        where no value has been set

        :returns: generator of mandatory Option's path
        """
        context = config_bag.context
        # copy
        od_setting_properties = config_bag.properties - {'mandatory', 'empty'}
        setting_properties = set(config_bag.properties) - {'warnings'}
        setting_properties.update(['mandatory', 'empty'])
        config_bag = ConfigBag(context=config_bag.context)
        config_bag.properties = frozenset(setting_properties)
        config_bag.set_permissive()
        od_config_bag = ConfigBag(context=config_bag.context)
        od_config_bag.properties = frozenset(od_setting_properties)
        od_config_bag.set_permissive()

        descr = context.cfgimpl_get_description()
        return self._mandatory_warnings(context,
                                        config_bag,
                                        descr,
                                        [],
                                        context,
                                        od_config_bag)

    #____________________________________________________________
    # default owner methods
    def set_context_owner(self,
                          owner):
        ":param owner: sets the default value for owner at the Config level"
        if owner in forbidden_owners:
            raise ValueError(_('set owner "{0}" is forbidden').format(str(owner)))

        self._p_.setowner(None,
                          owner,
                          index=None)

    def get_context_owner(self):
        return self._p_.getowner(None,
                                 None)
