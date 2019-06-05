# -*- coding: utf-8 -*-
# Copyright (C) 2012-2019 Team tiramisu (see AUTHORS for all contributors)
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
"options handler global entry point"
import weakref
from copy import copy


from .error import PropertiesOptionError, ConfigError, ConflictError, \
                   LeadershipError
from .option import SynDynOptionDescription, DynOptionDescription, Leadership
from .option.baseoption import BaseOption, valid_name
from .setting import OptionBag, ConfigBag, Settings, undefined
from .storage import get_storages, gen_storage_id, get_default_values_storages, list_sessions
from .value import Values
from .i18n import _


class SubConfig(object):
    """Sub configuration management entry.
    Tree if OptionDescription's responsability. SubConfig are generated
    on-demand. A Config is also a SubConfig.
    Root Config is call context below
    """
    __slots__ = ('_impl_context',
                 '_impl_descr',
                 '_impl_path',
                 '_impl_length')

    def __init__(self,
                 descr,
                 context,
                 config_bag,
                 subpath=None,
                 fromconsistency=None):
        """ Configuration option management class

        :param descr: describes the configuration schema
        :type descr: an instance of ``option.OptionDescription``
        :param context: the current root config
        :type context: `Config`
        :type subpath: `str` with the path name
        """
        # main option description
        if __debug__ and descr is not None and \
                (not isinstance(descr, (BaseOption, SynDynOptionDescription)) or
                 not descr.impl_is_optiondescription()):
            try:
                msg = descr.impl_get_displayname()
            except AttributeError:
                msg = descr
            raise TypeError(_('"{0}" must be an optiondescription, not an {1}'
                              ).format(msg, type(descr)))
        self._impl_descr = descr
        self._impl_context = context
        self._impl_path = subpath
        if descr is not None and descr.impl_is_leadership():
            leader = descr.get_leader()
            leaderpath = leader.impl_getname()
            full_leaderpath = self._get_subpath(leaderpath)
            cconfig_bag = config_bag.copy()
            cconfig_bag.remove_validation()
            moption_bag = OptionBag()
            moption_bag.set_option(leader,
                                   full_leaderpath,
                                   None,
                                   cconfig_bag)
            if fromconsistency:
                moption_bag.fromconsistency = fromconsistency
            value = self.getattr(leaderpath,
                                 moption_bag)
            self._impl_length = len(value)

    def cfgimpl_get_length(self):
        return self._impl_length

    def cfgimpl_get_length_leadership(self,
                                      option_bag):
        if option_bag.option.impl_is_symlinkoption():
            context = self.cfgimpl_get_context()
            path = option_bag.option.impl_getopt().impl_getpath()
            subconfig, _ = context.cfgimpl_get_home_by_path(path,
                                                            option_bag.config_bag)
            return subconfig.cfgimpl_get_length()
        else:
            return self.cfgimpl_get_length()

    def reset_one_option_cache(self,
                               desc,
                               values,
                               settings,
                               resetted_opts,
                               option_bag):

        if option_bag.path in resetted_opts:
            return
        resetted_opts.append(option_bag.path)
        for woption in option_bag.option._get_dependencies(self.cfgimpl_get_description()):
            option = woption()
            if option.impl_is_dynoptiondescription():
                subpath = option.impl_getpath().rsplit('.', 1)[0]
                for suffix in option.get_suffixes(option_bag.config_bag,
                                                  remove_none=True):
                    doption = option.to_dynoption(subpath,
                                                  suffix)
                    doption_path = doption.impl_getpath()
                    doption_bag = OptionBag()
                    doption_bag.set_option(doption,
                                           doption_path,
                                           option_bag.index,
                                           option_bag.config_bag)
                    self.reset_one_option_cache(desc,
                                                values,
                                                settings,
                                                resetted_opts,
                                                doption_bag)
            elif option.issubdyn():
                dynopt = option.getsubdyn()
                rootpath = dynopt.impl_getpath()
                subpaths = [rootpath] + option.impl_getpath()[len(rootpath) + 1:].split('.')[:-1]
                for suffix in dynopt.get_suffixes(option_bag.config_bag):
                    subpath = '.'.join([subp + suffix for subp in subpaths])
                    doption = option.to_dynoption(subpath,
                                                  suffix)
                    doption_path = doption.impl_getpath()
                    doption_bag = OptionBag()
                    doption_bag.set_option(doption,
                                           doption_path,
                                           option_bag.index,
                                           option_bag.config_bag)
                    self.reset_one_option_cache(desc,
                                                values,
                                                settings,
                                                resetted_opts,
                                                doption_bag)
            else:
                option_path = option.impl_getpath()
                doption_bag = OptionBag()
                doption_bag.set_option(option,
                                       option_path,
                                       option_bag.index,
                                       option_bag.config_bag)
                self.reset_one_option_cache(desc,
                                            values,
                                            settings,
                                            resetted_opts,
                                            doption_bag)
            del option
        option_bag.option.reset_cache(option_bag.path,
                                      values,
                                      settings,
                                      resetted_opts)

    def cfgimpl_reset_cache(self,
                            option_bag,
                            resetted_opts=None):
        """reset all settings in cache
        """
        if resetted_opts is None:
            resetted_opts = []

        context = self.cfgimpl_get_context()
        desc = context.cfgimpl_get_description()
        values = context.cfgimpl_get_values()
        settings = context.cfgimpl_get_settings()

        if option_bag is not None:
            self.reset_one_option_cache(desc,
                                        values,
                                        settings,
                                        resetted_opts,
                                        option_bag)
        else:
            values._p_.reset_all_cache()
            settings._p_.reset_all_cache()

    def cfgimpl_get_home_by_path(self,
                                 path,
                                 config_bag,
                                 fromconsistency=None):
        """:returns: tuple (config, name)"""
        path = path.split('.')
        for step in path[:-1]:
            option_bag = OptionBag()
            option = self.cfgimpl_get_description().get_child(step,
                                                              config_bag,
                                                              self.cfgimpl_get_path())
            subpath = self._get_subpath(step)
            option_bag.set_option(option,
                                  subpath,
                                  None,
                                  config_bag)
            if fromconsistency is not None:
                option_bag.fromconsistency = fromconsistency
            self = self.get_subconfig(option_bag)
        assert isinstance(self, SubConfig), _('unknown option {}').format(path[-1])
        return self, path[-1]

    # ______________________________________________________________________
    def cfgimpl_get_context(self):
        return self._impl_context()

    def cfgimpl_get_description(self):
        assert self._impl_descr is not None, _('there is no option description for this config'
                                               ' (may be GroupConfig)')
        return self._impl_descr

    def cfgimpl_get_settings(self):
        return self.cfgimpl_get_context()._impl_settings

    def cfgimpl_get_values(self):
        return self.cfgimpl_get_context()._impl_values

    def setattr(self,
                value,
                option_bag,
                _commit=True):

        if option_bag.option.impl_is_symlinkoption():
            raise ConfigError(_("can't assign to a SymLinkOption"))
        context = option_bag.config_bag.context
        context.cfgimpl_get_settings().validate_properties(option_bag)
        if option_bag.option.impl_is_leader() and len(value) < self._impl_length:
            raise LeadershipError(_('cannot reduce length of a leader "{}"'
                                    '').format(option_bag.option.impl_get_display_name()))
        return context.cfgimpl_get_values().setvalue(value,
                                                     option_bag,
                                                     _commit)

    def delattr(self,
                option_bag,
                _commit=True):
        option = option_bag.option
        if option.impl_is_symlinkoption():
            raise TypeError(_("can't delete a SymLinkOption"))
        values = self.cfgimpl_get_values()
        if option_bag.index is not None:
            values.reset_follower(option_bag,
                                  _commit)
        else:
            values.reset(option_bag,
                         _commit)

    def _get_subpath(self, name):
        if self._impl_path is None:
            subpath = name
        else:
            subpath = self._impl_path + '.' + name
        return subpath

    def get_subconfig(self,
                      option_bag):
        if option_bag.fromconsistency:
            fromconsistency = option_bag.fromconsistency.copy()
        else:
            fromconsistency = None

        self.cfgimpl_get_settings().validate_properties(option_bag)
        return SubConfig(option_bag.option,
                         self._impl_context,
                         option_bag.config_bag,
                         option_bag.path,
                         fromconsistency)

    def getattr(self,
                name,
                option_bag):
        """
        attribute notation mechanism for accessing the value of an option
        :param name: attribute name
        :return: option's value if name is an option name, OptionDescription
                 otherwise
        """
        config_bag = option_bag.config_bag
        if '.' in name:
            if option_bag.fromconsistency:
                fromconsistency = option_bag.fromconsistency.copy()
            else:
                fromconsistency = None
            self, name = self.cfgimpl_get_home_by_path(name,
                                                       config_bag,
                                                       fromconsistency)

        option = option_bag.option
        if option.impl_is_symlinkoption():
            soption_bag = OptionBag()
            soption_bag.set_option(option.impl_getopt(),
                                   None,
                                   option_bag.index,
                                   config_bag)
            soption_bag.ori_option = option
            context = self.cfgimpl_get_context()
            return context.getattr(soption_bag.path,
                                   soption_bag)

        self.cfgimpl_get_settings().validate_properties(option_bag)

        if option.impl_is_follower():
            length = self.cfgimpl_get_length_leadership(option_bag)
            follower_len = self.cfgimpl_get_values()._p_.get_max_length(option_bag.path)
            if follower_len > length:
                raise LeadershipError(_('follower option "{}" has higher length "{}" than the leader '
                                        'length "{}"').format(option.impl_get_display_name(),
                                                         follower_len,
                                                         length,
                                                         option_bag.index))
        if option.impl_is_follower() and option_bag.index is None:
            value = []
            for idx in range(length):
                soption_bag = OptionBag()
                soption_bag.set_option(option,
                                       option_bag.path,
                                       idx,
                                       config_bag)
                soption_bag.fromconsistency = option_bag.fromconsistency.copy()
                try:
                    value.append(self.getattr(name,
                                              soption_bag))
                except PropertiesOptionError as err:
                    value.append(err)
        else:
            value = self.cfgimpl_get_values().get_cached_value(option_bag)
        self.cfgimpl_get_settings().validate_mandatory(value,
                                                       option_bag)
        return value

    def find(self,
             bytype,
             byname,
             byvalue,
             config_bag,
             _subpath=None,
             raise_if_not_found=True,
             only_path=undefined,
             only_option=undefined,
             with_option=False):
        """
        convenience method for finding an option that lives only in the subtree

        :param first: return only one option if True, a list otherwise
        :return: find list or an exception if nothing has been found
        """
        def _filter_by_value(soption_bag):
            try:
                value = context.getattr(path,
                                     soption_bag)
            except PropertiesOptionError:
                return False
            if isinstance(value, list):
                return byvalue in value
            else:
                return value == byvalue

        found = False
        if only_path is not undefined:
            options = [only_option]
        else:
            options = self.cfgimpl_get_description().get_children_recursively(bytype,
                                                                              byname,
                                                                              config_bag)
        context = self.cfgimpl_get_context()
        for option in options:
            option_bag = OptionBag()
            path = option.impl_getpath()
            option_bag.set_option(option,
                                  path,
                                  None,
                                  config_bag)
            if byvalue is not undefined and not _filter_by_value(option_bag):
                continue
            elif config_bag.properties:
                #remove option with propertyerror, ...
                try:
                    if '.' in path:
                        subconfig, subpath = context.cfgimpl_get_home_by_path(path,
                                                                           config_bag)
                    else:
                        subconfig = self
                        subpath = path
                    subconfig.cfgimpl_get_description().get_child(subpath,
                                                                  config_bag,
                                                                  subconfig.cfgimpl_get_path())
                    self.cfgimpl_get_settings().validate_properties(option_bag)
                except PropertiesOptionError:
                    continue
            found = True
            if not with_option:
                yield path
            else:
                yield path, option
        self._find_return_results(found,
                                  raise_if_not_found)

    def _find_return_results(self,
                             found,
                             raise_if_not_found):
        if not found and raise_if_not_found:
            raise AttributeError(_("no option found in config"
                                   " with these criteria"))

    def make_dict(self,
                  config_bag,
                  flatten=False,
                  _currpath=None,
                  withoption=None,
                  withvalue=undefined,
                  fullpath=False):
        """exports the whole config into a `dict`, for example:

        >>> print(cfg.make_dict())
        {'od2.var4': None, 'od2.var5': None, 'od2.var6': None}



        :param flatten: returns a dict(name=value) instead of a dict(path=value)
                        ::

                            >>> print(cfg.make_dict(flatten=True))
                            {'var5': None, 'var4': None, 'var6': None}

        :param withoption: returns the options that are present in the very same
                           `OptionDescription` than the `withoption` itself::

                                >>> print(cfg.make_dict(withoption='var1'))
                                {'od2.var4': None, 'od2.var5': None,
                                'od2.var6': None,
                                'od2.var1': u'value',
                                'od1.var1': None,
                                'od1.var3': None,
                                'od1.var2': None}

        :param withvalue: returns the options that have the value `withvalue`
                          ::

                            >>> print(c.make_dict(withoption='var1',
                                                  withvalue=u'value'))
                            {'od2.var4': None,
                            'od2.var5': None,
                            'od2.var6': None,
                            'od2.var1': u'value'}

        :returns: dict of Option's name (or path) and values
        """
        pathsvalues = {}
        if _currpath is None:
            _currpath = []
        if withoption is None and withvalue is not undefined:
            raise ValueError(_("make_dict can't filtering with value without "
                               "option"))
        context = self.cfgimpl_get_context()
        self._make_dict(context,
                        config_bag,
                        flatten,
                        _currpath,
                        withoption,
                        withvalue,
                        fullpath,
                        pathsvalues)
        return pathsvalues

    def _make_dict(self,
                   context,
                   config_bag,
                   flatten,
                   _currpath,
                   withoption,
                   withvalue,
                   fullpath,
                   pathsvalues):
        if withoption is not None:
            # Find all option with criteria
            # retrieve OptionDescription and make_dict on it
            mypath = self.cfgimpl_get_path()
            for path in context.find(bytype=None,
                                     byname=withoption,
                                     byvalue=withvalue,
                                     _subpath=self.cfgimpl_get_path(False),
                                     config_bag=config_bag):
                path = '.'.join(path.split('.')[:-1])
                if '.' in path:
                    subconfig, subpath = context.cfgimpl_get_home_by_path(path,
                                                                          config_bag)
                else:
                    subconfig = context
                    subpath = path
                opt = subconfig.cfgimpl_get_description().get_child(subpath,
                                                                    config_bag,
                                                                    subconfig.cfgimpl_get_path())
                soption_bag = OptionBag()
                soption_bag.set_option(opt,
                                       path,
                                       None,
                                       config_bag)
                if mypath is not None:
                    if mypath == path:
                        withoption = None
                        withvalue = undefined
                        break
                    else:
                        tmypath = mypath + '.'
                        assert path.startswith(tmypath), _('unexpected path "{0}", '
                                                           'should start with "{1}"'
                                                           '').format(path, mypath)
                        path = path[len(tmypath):]
                self._make_sub_dict(path,
                                    pathsvalues,
                                    _currpath,
                                    flatten,
                                    soption_bag,
                                    fullpath,
                                    context,
                                    withvalue)

        #withoption can be set to None below !
        if withoption is None:
            for opt in self.cfgimpl_get_description().get_children(config_bag,
                                                                   context):
                name = opt.impl_getname()
                path = self._get_subpath(name)
                soption_bag = OptionBag()
                soption_bag.set_option(opt,
                                       path,
                                       None,
                                       config_bag)
                self._make_sub_dict(name,
                                    pathsvalues,
                                    _currpath,
                                    flatten,
                                    soption_bag,
                                    fullpath,
                                    context,
                                    withvalue)
        return pathsvalues

    def _make_sub_dict(self,
                       name,
                       pathsvalues,
                       _currpath,
                       flatten,
                       option_bag,
                       fullpath,
                       context,
                       withvalue):
        option = option_bag.option
        if option.impl_is_optiondescription():
            try:
                self.cfgimpl_get_settings().validate_properties(option_bag)
                subconfig = SubConfig(option_bag.option,
                                      self._impl_context,
                                      option_bag.config_bag,
                                      option_bag.path)
                subconfig._make_dict(context,
                                     option_bag.config_bag,
                                     flatten,
                                     _currpath + [name],
                                     None,
                                     withvalue,
                                     fullpath,
                                     pathsvalues)
            except PropertiesOptionError as err:
                if err.proptype == ['mandatory']:
                    raise err
                pass
        else:
            try:
                ret = self.getattr(name,
                                   option_bag)
            except PropertiesOptionError as err:
                if err.proptype == ['mandatory']:
                    raise err
                return
            if flatten:
                name_ = option.impl_getname()
            elif fullpath:
                name_ = self._get_subpath(name)
            else:
                name_ = '.'.join(_currpath + [name])
            pathsvalues[name_] = ret

    def cfgimpl_get_path(self,
                         dyn=True):
        descr = self.cfgimpl_get_description()
        if not dyn and descr.impl_is_dynoptiondescription():
            return descr.impl_getopt().impl_getpath()
        return self._impl_path


class _CommonConfig(SubConfig):
    "abstract base class for the Config, KernelGroupConfig and the KernelMetaConfig"
    __slots__ = ('_impl_values',
                 '_impl_settings',
                 '_impl_meta',
                 'impl_type')

    def _impl_build_all_caches(self):
        descr = self.cfgimpl_get_description()
        if not descr.impl_already_build_caches():
            descr._build_cache()
        config_bag = ConfigBag(context=self)
        descr.impl_build_force_store_values(config_bag)

    def cfgimpl_get_meta(self):
        if self._impl_meta is not None:
            return self._impl_meta()

    # information
    def impl_set_information(self, key, value):
        """updates the information's attribute

        :param key: information's key (ex: "help", "doc"
        :param value: information's value (ex: "the help string")
        """
        self._impl_values.set_information(key, value)

    def impl_get_information(self, key, default=undefined):
        """retrieves one information's item

        :param key: the item string (ex: "help")
        """
        return self._impl_values.get_information(key, default)

    def impl_del_information(self, key, raises=True):
        self._impl_values.del_information(key, raises)

    def impl_list_information(self):
        return self._impl_values.list_information()

    def __getstate__(self):
        raise NotImplementedError()

    def _gen_fake_values(self):
        fake_config = KernelConfig(self._impl_descr,
                                   persistent=False,
                                   force_values=get_default_values_storages(),
                                   force_settings=self.cfgimpl_get_settings())
        fake_config.cfgimpl_get_values()._p_.importation(self.cfgimpl_get_values()._p_.exportation())
        return fake_config

    def duplicate(self,
                  session_id=None,
                  force_values=None,
                  force_settings=None,
                  storage=None,
                  persistent=False,
                  metaconfig_prefix=None,
                  child=None,
                  deep=False):
        assert isinstance(self, (KernelConfig, KernelMixConfig)), _('cannot duplicate {}').format(self.__class__.__name__)
        if isinstance(self, KernelConfig):
            duplicated_config = KernelConfig(self._impl_descr,
                                             _duplicate=True,
                                             session_id=session_id,
                                             force_values=force_values,
                                             force_settings=force_settings,
                                             persistent=persistent,
                                             storage=storage)
        else:
            if session_id is None and metaconfig_prefix is not None:
                session_id = metaconfig_prefix + self.impl_getname()
            duplicated_config = KernelMetaConfig([],
                                                 _duplicate=True,
                                                 optiondescription=self._impl_descr,
                                                 session_id=session_id,
                                                 persistent=persistent,
                                                 storage=storage)
        duplicated_config.cfgimpl_get_values()._p_.importation(self.cfgimpl_get_values()._p_.exportation())
        properties = self.cfgimpl_get_settings()._p_.exportation()
        duplicated_config.cfgimpl_get_settings()._p_.importation(properties)
        duplicated_config.cfgimpl_get_settings()._pp_.importation(self.cfgimpl_get_settings(
            )._pp_.exportation())
        duplicated_config.cfgimpl_reset_cache(None, None)
        if child is not None:
            duplicated_config._impl_children.append(child)
            child._impl_meta = weakref.ref(duplicated_config)
        if self._impl_meta:
            if deep:
                duplicated_config = self._impl_meta().duplicate(deep=deep,
                                                                storage=storage,
                                                                metaconfig_prefix=metaconfig_prefix,
                                                                child=duplicated_config,
                                                                persistent=persistent)
            else:
                duplicated_config._impl_meta = self._impl_meta
                self._impl_meta()._impl_children.append(duplicated_config)
        return duplicated_config


# ____________________________________________________________
class KernelConfig(_CommonConfig):
    "main configuration management entry"
    __slots__ = ('__weakref__',
                 '_impl_name')
    impl_type = 'config'

    def __init__(self,
                 descr,
                 session_id=None,
                 persistent=False,
                 force_values=None,
                 force_settings=None,
                 _duplicate=False,
                 storage=None):
        """ Configuration option management class

        :param descr: describes the configuration schema
        :type descr: an instance of ``option.OptionDescription``
        :param context: the current root config
        :type context: `Config`
        :param session_id: session ID is import with persistent Config to
        retrieve good session
        :type session_id: `str`
        :param persistent: if persistent, don't delete storage when leaving
        :type persistent: `boolean`
        """
        self._impl_meta = None
        if isinstance(descr, Leadership):
            raise ConfigError(_('cannot set leadership object has root optiondescription'))
        if isinstance(descr, DynOptionDescription):
            raise ConfigError(_('cannot set dynoptiondescription object has root optiondescription'))
        if force_settings is not None and force_values is not None:
            if isinstance(force_settings, tuple):
                self._impl_settings = Settings(force_settings[0],
                                               force_settings[1])
            else:
                self._impl_settings = force_settings
            self._impl_values = Values(force_values)
        else:
            properties, permissives, values, session_id = get_storages(self,
                                                                       session_id,
                                                                       persistent,
                                                                       storage=storage)
            if not valid_name(session_id):
                raise ValueError(_("invalid session ID: {0} for config").format(session_id))
            self._impl_settings = Settings(properties,
                                           permissives)
            self._impl_values = Values(values)
        super().__init__(descr,
                         weakref.ref(self),
                         ConfigBag(self),
                         None)
        if None in [force_settings, force_values]:
            self._impl_build_all_caches()
        self._impl_name = session_id

    def impl_getname(self):
        return self._impl_name

    def cfgimpl_get_config_path(self):
        if self._impl_meta is None or self._impl_meta() is None:
            return self._impl_name
        return self._impl_meta().cfgimpl_get_config_path() + '.' + self._impl_name


class KernelGroupConfig(_CommonConfig):
    __slots__ = ('__weakref__',
                 '_impl_children',
                 '_impl_name')
    impl_type = 'group'

    def __init__(self,
                 children,
                 session_id=None,
                 _descr=None):
        assert isinstance(children, list), _("groupconfig's children must be a list")
        names = []
        for child in children:
            assert isinstance(child,
                              _CommonConfig), _("groupconfig's children must be Config, MetaConfig or GroupConfig")
            name_ = child._impl_name
            names.append(name_)
        if len(names) != len(set(names)):
            for idx in range(1, len(names) + 1):
                name = names.pop(0)
                if name in names:
                    raise ConflictError(_('config name must be uniq in '
                                          'groupconfig for "{0}"').format(name))
        self._impl_children = children
        self._impl_meta = None
        session_id = gen_storage_id(session_id, self)
        assert valid_name(session_id), _("invalid session ID: {0} for config").format(session_id)
        super().__init__(_descr,
                         weakref.ref(self),
                         ConfigBag(self),
                         None)
        self._impl_name = session_id

    def cfgimpl_get_children(self):
        return self._impl_children

    def cfgimpl_reset_cache(self,
                            option_bag,
                            resetted_opts=None):
        if resetted_opts is None:
            resetted_opts = []
        if isinstance(self, KernelMixConfig):
            super().cfgimpl_reset_cache(option_bag,
                                        resetted_opts=copy(resetted_opts))
        for child in self._impl_children:
            if option_bag is not None:
                coption_bag = option_bag.copy()
                cconfig_bag = coption_bag.config_bag.copy()
                cconfig_bag.context = child
                coption_bag.config_bag = cconfig_bag
            else:
                coption_bag = None
            child.cfgimpl_reset_cache(coption_bag,
                                      resetted_opts=copy(resetted_opts))

    def set_value(self,
                  path,
                  index,
                  value,
                  config_bag,
                  only_config=False,
                  _commit=True):
        """Setattr not in current KernelGroupConfig, but in each children
        """
        ret = []
        if self.impl_type == 'group':
            # No value so cannot commit only one time
            commit = True
        else:
            # Commit only one time
            commit = False
        for child in self._impl_children:
            cconfig_bag = config_bag.copy()
            cconfig_bag.context = child
            if isinstance(child, KernelGroupConfig):
                ret.extend(child.set_value(path,
                                           index,
                                           value,
                                           cconfig_bag,
                                           only_config=only_config,
                                           _commit=commit))
            else:
                try:
                    subconfig, name = child.cfgimpl_get_home_by_path(path,
                                                                     cconfig_bag)
                    option = subconfig.cfgimpl_get_description().get_child(name,
                                                                           cconfig_bag,
                                                                           child.cfgimpl_get_path())
                    option_bag = OptionBag()
                    option_bag.set_option(option,
                                          path,
                                          index,
                                          cconfig_bag)
                    child.setattr(value,
                                  option_bag,
                                  _commit=commit)
                except PropertiesOptionError as err:
                    ret.append(PropertiesOptionError(err._option_bag,
                                                     err.proptype,
                                                     err._settings,
                                                     err._opt_type,
                                                     err._requires,
                                                     err._name,
                                                     err._orig_opt))
                except (ValueError, LeadershipError, AttributeError) as err:
                    ret.append(err)
        if _commit and self.impl_type != 'group':
            self.cfgimpl_get_values()._p_.commit()
        return ret


    def find_group(self,
                   config_bag,
                   byname=None,
                   bypath=undefined,
                   byoption=undefined,
                   byvalue=undefined,
                   raise_if_not_found=True,
                   _sub=False):
        """Find first not in current KernelGroupConfig, but in each children
        """
        # if KernelMetaConfig, all children have same OptionDescription in
        # context so search only one time the option for all children
        if bypath is undefined and byname is not None and \
                isinstance(self,
                           KernelMixConfig):
            bypath, byoption = next(self.find(bytype=None,
                                              byvalue=undefined,
                                              byname=byname,
                                              config_bag=config_bag,
                                              raise_if_not_found=raise_if_not_found,
                                              with_option=True))
            byname = None

        ret = []
        for child in self._impl_children:
            if isinstance(child, KernelGroupConfig):
                ret.extend(child.find_group(byname=byname,
                                            bypath=bypath,
                                            byoption=byoption,
                                            byvalue=byvalue,
                                            config_bag=config_bag,
                                            raise_if_not_found=False,
                                            _sub=True))
            else:
                try:
                    cconfig_bag = config_bag.copy()
                    cconfig_bag.context = child
                    next(child.find(None,
                                    byname,
                                    byvalue,
                                    config_bag=cconfig_bag,
                                    raise_if_not_found=False,
                                    only_path=bypath,
                                    only_option=byoption))
                    ret.append(child)
                except StopIteration:
                    pass
        if not _sub:
            self._find_return_results(ret != [],
                                      raise_if_not_found)
        return ret

    def impl_getname(self):
        return self._impl_name

    def reset(self,
              path,
              _commit=True):
        for child in self._impl_children:
            config_bag = ConfigBag(child)
            config_bag.remove_validation()
            subconfig, name = child.cfgimpl_get_home_by_path(path,
                                                             config_bag)
            option = subconfig.cfgimpl_get_description().get_child(name,
                                                                   config_bag,
                                                                   subconfig.cfgimpl_get_path())
            option_bag = OptionBag()
            option_bag.set_option(option,
                                  path,
                                  option,
                                  config_bag)
            option_bag.config_bag.context = child
            child.cfgimpl_get_values().reset(option_bag,
                                             _commit=_commit)

    def getconfig(self,
                  name):
        for child in self._impl_children:
            if name == child.impl_getname():
                return child
        raise ConfigError(_('unknown config "{}"').format(name))

    def cfgimpl_get_config_path(self):
        if self._impl_meta is None or self._impl_meta() is None:
            return self._impl_name
        return self._impl_meta().cfgimpl_get_config_path() + '.' + self._impl_name


class KernelMixConfig(KernelGroupConfig):
    __slots__ = tuple()
    impl_type = 'mix'

    def __init__(self,
                 optiondescription,
                 children,
                 session_id=None,
                 persistent=False,
                 storage=None,
                 _duplicate=False):
        # FIXME _duplicate
        for child in children:
            if not isinstance(child, _CommonConfig):
                try:
                    child = child._config
                except:
                    raise TypeError(_("{}config's children "
                                      "should be config, not {}"
                                      ).format(self.impl_type,
                                               type(child)))
            if not isinstance(child, (KernelConfig, KernelMixConfig)):
                raise TypeError(_("child must be a Config, MixConfig or MetaConfig"))
            if child.cfgimpl_get_meta() is not None:
                raise ValueError(_("child has already a {}config's").format(self.impl_type))
            child._impl_meta = weakref.ref(self)
        properties, permissives, values, session_id = get_storages(self,
                                                                   session_id,
                                                                   persistent,
                                                                   storage=storage)
        self._impl_settings = Settings(properties,
                                       permissives)
        self._impl_values = Values(values)
        super().__init__(children,
                         session_id=session_id,
                         _descr=optiondescription)
        self._impl_build_all_caches()

    def set_value(self,
                  path,
                  index,
                  value,
                  config_bag,
                  force_default=False,
                  force_dont_change_value=False,
                  force_default_if_same=False,
                  only_config=False,
                  _commit=True):
        """only_config: could be set if you want modify value in all Config included in
                        this KernelMetaConfig
        """
        if only_config:
            if force_default or force_default_if_same or force_dont_change_value:
                raise ValueError(_('force_default, force_default_if_same or '
                                   'force_dont_change_value cannot be set with'
                                   ' only_config'))
            return super().set_value(path,
                                     index,
                                     value,
                                     config_bag,
                                     only_config=only_config,
                                     _commit=_commit)
        ret = []
        subconfig, name = self.cfgimpl_get_home_by_path(path,
                                                        config_bag)
        option = subconfig.cfgimpl_get_description().get_child(name,
                                                               config_bag,
                                                               self.cfgimpl_get_path())
        option_bag = OptionBag()
        option_bag.set_option(option,
                              path,
                              index,
                              config_bag)
        if force_default or force_default_if_same or force_dont_change_value:
            if force_default and force_dont_change_value:
                raise ValueError(_('force_default and force_dont_change_value'
                                   ' cannot be set together'))
            for child in self._impl_children:
                cconfig_bag = config_bag.copy()
                cconfig_bag.context = child
                try:
                    subconfig2, name = child.cfgimpl_get_home_by_path(path,
                                                                      cconfig_bag)
                    if self.impl_type == 'meta':
                        moption_bag = option_bag
                        del moption_bag.properties
                        del moption_bag.permissives
                        moption_bag.config_bag = cconfig_bag
                    else:
                        option = subconfig2.cfgimpl_get_description().get_child(name,
                                                                                cconfig_bag,
                                                                                child.cfgimpl_get_path())
                        moption_bag = OptionBag()
                        moption_bag.set_option(option,
                                               path,
                                               index,
                                               cconfig_bag)
                    if force_default_if_same:
                        if not child.cfgimpl_get_values()._p_.hasvalue(path):
                            child_value = undefined
                        else:
                            child_value = subconfig2.getattr(name,
                                                             moption_bag)
                    if force_default or (force_default_if_same and value == child_value):
                        child.cfgimpl_get_values().reset(moption_bag,
                                                         _commit=False)
                        continue
                    if force_dont_change_value:
                        child_value = child.getattr(name,
                                                    moption_bag)
                        if value != child_value:
                            subconfig2.setattr(child_value,
                                               moption_bag,
                                               _commit=False)
                except PropertiesOptionError as err:
                    ret.append(PropertiesOptionError(err._option_bag,
                                                     err.proptype,
                                                     err._settings,
                                                     err._opt_type,
                                                     err._requires,
                                                     err._name,
                                                     err._orig_opt))
                except (ValueError, LeadershipError, AttributeError) as err:
                    ret.append(err)

        try:
            if self.impl_type == 'meta':
                del option_bag.properties
                del option_bag.permissives
                option_bag.config_bag = config_bag
            subconfig.setattr(value,
                              option_bag,
                              _commit=False)
        except (PropertiesOptionError, ValueError, LeadershipError) as err:
            ret.append(err)
        return ret

    def reset(self,
              path,
              only_children,
              config_bag,
              commit=True):
        rconfig_bag = config_bag.copy()
        rconfig_bag.remove_validation()
        if self.impl_type == 'meta':
            subconfig, name = self.cfgimpl_get_home_by_path(path,
                                                            config_bag)
            option = subconfig.cfgimpl_get_description().get_child(name,
                                                                   config_bag,
                                                                   subconfig.cfgimpl_get_path())
            option_bag = OptionBag()
            option_bag.set_option(option,
                                  path,
                                  None,
                                  rconfig_bag)
        elif not only_children:
            try:
                subconfig, name = self.cfgimpl_get_home_by_path(path,
                                                                config_bag)
                option = subconfig.cfgimpl_get_description().get_child(name,
                                                                       config_bag,
                                                                       subconfig.cfgimpl_get_path())
                option_bag = OptionBag()
                option_bag.set_option(option,
                                      path,
                                      None,
                                      rconfig_bag)
            except AttributeError:
                only_children = True
        for child in self._impl_children:
            rconfig_bag.context = child
            try:
                if self.impl_type == 'meta':
                    moption_bag = option_bag
                    moption_bag.config_bag = rconfig_bag
                else:
                    subconfig, name = child.cfgimpl_get_home_by_path(path,
                                                                     rconfig_bag)
                    option = subconfig.cfgimpl_get_description().get_child(name,
                                                                           rconfig_bag,
                                                                           child.cfgimpl_get_path())
                    moption_bag = OptionBag()
                    moption_bag.set_option(option,
                                           path,
                                           None,
                                           rconfig_bag)
                child.cfgimpl_get_values().reset(moption_bag,
                                                 _commit=False)
            except AttributeError:
                pass
            if isinstance(child, KernelMixConfig):
                child.reset(path,
                            False,
                            rconfig_bag,
                            commit=False)
        if not only_children:
            option_bag.config_bag = config_bag
            self.cfgimpl_get_values().reset(option_bag,
                                            _commit=False)
        if commit:
            self.cfgimpl_get_values()._p_.commit()

    def add_config(self,
                   apiconfig):
        config = apiconfig._config_bag.context
        if config._impl_meta is not None:
            raise ConflictError(_('config is already in a metaconfig'))
        if config.impl_getname() in [child.impl_getname() for child in self._impl_children]:
            raise ConflictError(_('config name must be uniq in '
                                  'groupconfig for {0}').format(config.impl_getname()))

        config._impl_meta = weakref.ref(self)
        self._impl_children.append(config)
        config.cfgimpl_reset_cache(None, None)

    def pop_config(self,
                   session_id):
        for idx, child in enumerate(self._impl_children):
            if session_id == child.impl_getname():
                child._impl_meta = None
                child.cfgimpl_reset_cache(None, None)
                return self._impl_children.pop(idx)
        raise ConfigError(_('cannot find the config {}').format(session_id))


class KernelMetaConfig(KernelMixConfig):
    __slots__ = tuple()
    impl_type = 'meta'

    def __init__(self,
                 children,
                 session_id=None,
                 persistent=False,
                 optiondescription=None,
                 storage=None,
                 _duplicate=False):
        descr = None
        if optiondescription is not None:
            if not _duplicate:
                new_children = []
                for child_session_id in children:
                    assert isinstance(child_session_id, str), _('MetaConfig with optiondescription'
                                                                ' must have string has child, '
                                                                'not {}').format(child_session_id)
                    new_children.append(KernelConfig(optiondescription,
                                                     persistent=persistent,
                                                     session_id=child_session_id))
                children = new_children
            descr = optiondescription
        for child in children:
            if not isinstance(child, _CommonConfig):
                try:
                    child = child._config
                except Exception:
                    raise TypeError(_("{}config's children "
                                      "should be config, not {}"
                                      ).format(self.impl_type,
                                               type(child)))
            if __debug__ and not isinstance(child, (KernelConfig,
                                                    KernelMetaConfig)):
                raise TypeError(_("child must be a Config or MetaConfig"))
            if descr is None:
                descr = child.cfgimpl_get_description()
            elif descr is not child.cfgimpl_get_description():
                raise ValueError(_('all config in metaconfig must '
                                   'have the same optiondescription'))
        super().__init__(descr,
                         children,
                         persistent=persistent,
                         storage=storage,
                         session_id=session_id)

    def new_config(self,
                   session_id,
                   type_='config',
                   persistent=False):
        if session_id in [child.impl_getname() for child in self._impl_children]:
            raise ConflictError(_('config name must be uniq in '
                                  'groupconfig for {0}').format(session_id))
        assert type_ in ('config', 'metaconfig', 'mixconfig'), _('unknown type {}').format(type_)
        new = not persistent or session_id not in list_sessions()
        if type_ == 'config':
            config = KernelConfig(self._impl_descr,
                                  session_id=session_id,
                                  persistent=persistent)
        elif type_ == 'metaconfig':
            config = KernelMetaConfig([],
                                      optiondescription=self._impl_descr,
                                      session_id=session_id,
                                      persistent=persistent)
        elif type_ == 'mixconfig':
            config = KernelMixConfig(children=[],
                                     optiondescription=self._impl_descr,
                                     session_id=session_id,
                                     persistent=persistent)
        # Copy context properties/permissives
        if new:
            config.cfgimpl_get_settings().set_context_properties(self.cfgimpl_get_settings().get_context_properties(), config)
            config.cfgimpl_get_settings().set_context_permissives(self.cfgimpl_get_settings().get_context_permissives())

        config._impl_meta = weakref.ref(self)
        self._impl_children.append(config)
        return config

    def add_config(self,
                   apiconfig):
        if self._impl_descr is not apiconfig._config_bag.context.cfgimpl_get_description():
            raise ValueError(_('metaconfig must '
                               'have the same optiondescription'))
        super().add_config(apiconfig)
