# -*- coding: utf-8 -*-
"sets the options of the configuration objects Config object itself"
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
# ____________________________________________________________
from .error import (RequirementError, PropertiesOptionError,
                    ConstError, ConfigError, display_list)
from .i18n import _


"""If cache and expire is enable, time before cache is expired.
This delay start first time value/setting is set in cache, even if
user access several time to value/setting
"""
EXPIRATION_TIME = 5
"""List of default properties (you can add new one if needed).

For common properties and personalise properties, if a propery is set for
an Option and for the Config together, Setting raise a PropertiesOptionError

* Common properties:

hidden
    option with this property can only get value in read only mode. This
    option is not available in read write mode.

disabled
    option with this property cannot be set/get

frozen
    cannot set value for option with this properties if 'frozen' is set in
    config

mandatory
    should set value for option with this properties if 'mandatory' is set in
    config


* Special property:

permissive
    option with 'permissive' cannot raise PropertiesOptionError for properties
    set in permissive
    config with 'permissive', whole option in this config cannot raise
    PropertiesOptionError for properties set in permissive

* Special Config properties:

cache
    if set, enable cache settings and values

expire
    if set, settings and values in cache expire after ``expiration_time``

everything_frozen
    whole option in config are frozen (even if option have not frozen
    property)

empty
    raise mandatory PropertiesOptionError if multi or leader have empty value

validator
    launch validator set by user in option (this property has no effect
    for internal validator)

warnings
    display warnings during validation

demoting_error_warning
    all value errors are convert to warning (ValueErrorWarning)
"""
DEFAULT_PROPERTIES = frozenset(['cache', 'validator', 'warnings'])
SPECIAL_PROPERTIES = {'frozen', 'mandatory', 'empty', 'force_store_value'}

"""Config can be in two defaut mode:

read_only
    you can get all variables not disabled but you cannot set any variables
    if a value has a callback without any value, callback is launch and value
    of this variable can change
    you cannot access to mandatory variable without values

read_write
    you can get all variables not disabled and not hidden
    you can set all variables not frozen
"""
RO_APPEND = frozenset(['frozen', 'disabled', 'validator', 'everything_frozen',
                       'mandatory', 'empty', 'force_store_value'])
RO_REMOVE = frozenset(['permissive', 'hidden'])
RW_APPEND = frozenset(['frozen', 'disabled', 'validator', 'hidden',
                      'force_store_value'])
RW_REMOVE = frozenset(['permissive', 'everything_frozen', 'mandatory',
                       'empty'])


FORBIDDEN_SET_PROPERTIES = frozenset(['force_store_value'])
FORBIDDEN_SET_PERMISSIVES = frozenset(['force_default_on_freeze',
                                       'force_metaconfig_on_freeze',
                                       'force_store_value'])


static_set = frozenset()


class OptionBag:
    __slots__ = ('option',  # current option
                 'path',
                 'index',
                 'config_bag',
                 'ori_option',  # original option (for example useful for symlinkoption)
                 'properties',  # properties of current option
                 'apply_requires',  # apply requires or not for this option
                 'fromconsistency'  # history for consistency
                 )

    def __init__(self):
        self.option = None
        self.fromconsistency = []

    def set_option(self,
                   option,
                   path,
                   index,
                   config_bag):
        if path is None:
            path = option.impl_getpath()
        self.path = path
        self.index = index
        self.option = option
        self.config_bag = config_bag

    def __getattr__(self, key):
        if key == 'properties':
            settings = self.config_bag.context.cfgimpl_get_settings()
            self.properties = settings.getproperties(self,
                                                     apply_requires=self.apply_requires)
            return self.properties
        elif key == 'ori_option':
            return self.option
        elif key == 'apply_requires':
            return True
        raise KeyError('unknown key {} for OptionBag'.format(key))  # pragma: no cover

    def __delattr__(self, key):
        if key in ['properties', 'permissives']:
            try:
                super().__delattr__(key)
            except AttributeError:
                pass
            return
        raise KeyError('unknown key {} for ConfigBag'.format(key))  # pragma: no cover

    def copy(self):
        option_bag = OptionBag()
        for key in self.__slots__:
            if key == 'properties' and self.config_bag is undefined:
                continue
            setattr(option_bag, key, getattr(self, key))
        return option_bag


class ConfigBag:
    __slots__ = ('context',  # link to the current context
                 'properties',  # properties for current context
                 'true_properties',  # properties for current context
                 'permissives',  # permissives for current context
                 'expiration_time'  # EXPIRATION_TIME
                 )

    def __init__(self, context, **kwargs):
        self.context = context
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, key):
        if key == 'properties':
            settings = self.context.cfgimpl_get_settings()
            self.properties = settings.get_context_properties()
            return self.properties
        if key == 'permissives':
            settings = self.context.cfgimpl_get_settings()
            self.permissives = settings.get_context_permissives()
            return self.permissives
        if key == 'true_properties':
            return self.properties
        if key == 'expiration_time':
            self.expiration_time = EXPIRATION_TIME
            return self.expiration_time
        raise KeyError('unknown key {} for ConfigBag'.format(key))  # pragma: no cover

    def remove_warnings(self):
        self.properties = frozenset(self.properties - {'warnings'})

    def remove_validation(self):
        self.properties = frozenset(self.properties - {'validator'})

    def unrestraint(self):
        self.true_properties = self.properties
        self.properties = frozenset(['cache'])

    def set_permissive(self):
        self.properties = frozenset(self.properties | {'permissive'})

    def __delattr__(self, key):
        if key in ['properties', 'permissives']:
            try:
                super().__delattr__(key)
            except AttributeError:
                pass
            return
        raise KeyError('unknown key {} for ConfigBag'.format(key))  # pragma: no cover

    # def __setattr__(self, key, value):
    #     super().__setattr__(key, value)

    def copy(self):
        kwargs = {}
        for key in self.__slots__:
            if key in ['properties', 'permissives', 'true_properties'] and \
                    not hasattr(self.context, '_impl_settings'):
                # not for GroupConfig
                continue
            kwargs[key] = getattr(self, key)
        return ConfigBag(**kwargs)


# ____________________________________________________________
class _NameSpace(object):
    """convenient class that emulates a module
    and builds constants (that is, unique names)
    when attribute is added, we cannot delete it
    """

    def __setattr__(self,
                    name,
                    value):
        if name in self.__dict__:
            raise ConstError(_("can't rebind {0}").format(name))
        self.__dict__[name] = value

    def __delattr__(self,
                    name):
        raise ConstError(_("can't unbind {0}").format(name))


class GroupModule(_NameSpace):
    "emulates a module to manage unique group (OptionDescription) names"
    class GroupType(str):
        """allowed normal group (OptionDescription) names
        *normal* means : groups that are not leader
        """
        pass

    class DefaultGroupType(GroupType):
        """groups that are default (typically 'default')"""
        pass

    class LeadershipGroupType(GroupType):
        """allowed normal group (OptionDescription) names
        *leadership* means : groups that have the 'leadership' attribute set
        """
        pass


class OwnerModule(_NameSpace):
    """emulates a module to manage unique owner names.

    owners are living in `Config._cfgimpl_value_owners`
    """
    class Owner(str):
        """allowed owner names
        """
        pass

    class DefaultOwner(Owner):
        """groups that are default (typically 'default')"""
        pass

    def addowner(self, name):
        """
        :param name: the name of the new owner
        """
        setattr(owners, name, owners.Owner(name))


# ____________________________________________________________
# populate groups
groups = GroupModule()
"""groups.default
        default group set when creating a new optiondescription"""
groups.default = groups.DefaultGroupType('default')

"""groups.leadership
        leadership group is a special optiondescription, all suboptions should
        be multi option and all values should have same length, to find
        leader's option, the optiondescription's name should be same than de
        leader's option"""
groups.leadership = groups.LeadershipGroupType('leadership')

"""    groups.family
        example of group, no special behavior with this group's type"""
groups.family = groups.GroupType('family')


# ____________________________________________________________
# populate owners with default attributes
owners = OwnerModule()
"""default
        is the config owner after init time"""
owners.default = owners.DefaultOwner('default')
"""user
        is the generic is the generic owner"""
owners.user = owners.Owner('user')
"""forced
        special owner when value is forced"""
owners.forced = owners.Owner('forced')


forbidden_owners = (owners.default, owners.forced)


# ____________________________________________________________
class Undefined(object):
    def __str__(self):  # pragma: no cover
        return 'Undefined'

    __repr__ = __str__


undefined = Undefined()


# ____________________________________________________________
class Settings(object):
    "``config.Config()``'s configuration options settings"
    __slots__ = ('_p_',
                 '_pp_',
                 '__weakref__',
                 'ro_append',
                 'ro_remove',
                 'rw_append',
                 'rw_remove',
                 'default_properties')

    def __init__(self,
                 properties,
                 permissives):
        """
        initializer

        :param context: the root config
        :param storage: the storage type

                        - dictionary -> in memory
                        - sqlite3 -> persistent
        """
        # generic owner
        self._p_ = properties
        self._pp_ = permissives
        self.default_properties = DEFAULT_PROPERTIES
        self.ro_append = RO_APPEND
        self.ro_remove = RO_REMOVE
        self.rw_append = RW_APPEND
        self.rw_remove = RW_REMOVE

    # ____________________________________________________________
    # get properties and permissive methods

    def get_context_properties(self):
        is_cached, props = self._p_.getcache(None,
                                             None,
                                             None,
                                             {},
                                             {},
                                             'context_props')
        if not is_cached:
            props = self._p_.getproperties(None,
                                           self.default_properties)
            self._p_.setcache(None,
                              None,
                              props,
                              {},
                              props)
        return props

    def getproperties(self,
                      option_bag,
                      apply_requires=True):
        """
        """
        opt = option_bag.option
        config_bag = option_bag.config_bag
        path = option_bag.path
        index = option_bag.index
        if opt.impl_is_symlinkoption():
            opt = opt.impl_getopt()
            path = opt.impl_getpath()

        if apply_requires:
            props = config_bag.properties
            is_cached, props = self._p_.getcache(path,
                                                 config_bag.expiration_time,
                                                 index,
                                                 props,
                                                 {},
                                                 'self_props')
        else:
            is_cached = False
        if not is_cached:
            props = self._p_.getproperties(path,
                                           opt.impl_getproperties())
            if apply_requires:
                props |= self.apply_requires(option_bag,
                                             False)
            props -= self.getpermissives(opt,
                                         path)
            if apply_requires:
                self._p_.setcache(path,
                                  index,
                                  props,
                                  props,
                                  config_bag.properties)
        return props

    def get_context_permissives(self):
        return self.getpermissives(None, None)

    def getpermissives(self,
                       opt,
                       path):
        if opt and opt.impl_is_symlinkoption():
            opt = opt.impl_getopt()
            path = opt.impl_getpath()
        return self._pp_.getpermissives(path)

    def apply_requires(self,
                       option_bag,
                       readable):
        """carries out the jit (just in time) requirements between options

        a requirement is a tuple of this form that comes from the option's
        requirements validation::

            (option, expected, action, inverse, transitive, same_action)

        let's have a look at all the tuple's items:

        - **option** is the target option's

        - **expected** is the target option's value that is going to trigger
          an action

        - **action** is the (property) action to be accomplished if the target
          option happens to have the expected value

        - if **inverse** is `True` and if the target option's value does not
          apply, then the property action must be removed from the option's
          properties list (wich means that the property is inverted)

        - **transitive**: but what happens if the target option cannot be
          accessed ? We don't kown the target option's value. Actually if some
          property in the target option is not present in the permissive, the
          target option's value cannot be accessed. In this case, the
          **action** have to be applied to the option. (the **action** property
          is then added to the option).

        - **same_action**: actually, if **same_action** is `True`, the
          transitivity is not accomplished. The transitivity is accomplished
          only if the target option **has the same property** that the demanded
          action. If the target option's value is not accessible because of
          another reason, because of a property of another type, then an
          exception :exc:`~error.RequirementError` is raised.

        And at last, if no target option matches the expected values, the
        action will not add to the option's properties list.

        :param opt: the option on wich the requirement occurs
        :type opt: `option.Option()`
        :param path: the option's path in the config
        :type path: str
        """
        current_requires = option_bag.option.impl_getrequires()

        # filters the callbacks
        if readable:
            calc_properties = {}
        else:
            calc_properties = set()

        if not current_requires:
            return calc_properties

        context = option_bag.config_bag.context
        all_properties = None
        for requires in current_requires:
            for require in requires:
                exps, action, inverse, transitive, same_action, operator = require
                breaked = False
                for option, expected in exps:
                    if not isinstance(option, tuple):
                        if option.issubdyn():
                            option = option.to_dynoption(option_bag.option.rootpath,
                                                         option_bag.option.impl_getsuffix())
                        reqpath = option.impl_getpath()
                        if __debug__ and reqpath.startswith(option_bag.path + '.'):
                            # FIXME too later!
                            raise RequirementError(_("malformed requirements "
                                                     "imbrication detected for option:"
                                                     " '{0}' with requirement on: "
                                                     "'{1}'").format(option_bag.path, reqpath))
                        idx = None
                        is_indexed = False
                        if option.impl_is_follower():
                            idx = option_bag.index
                            if idx is None:
                                continue
                        elif option.impl_is_leader() and option_bag.index is None:
                            continue
                        elif option.impl_is_multi() and option_bag.index is not None:
                            is_indexed = True
                        config_bag = option_bag.config_bag.copy()
                        soption_bag = OptionBag()
                        soption_bag.set_option(option,
                                               reqpath,
                                               idx,
                                               config_bag)
                        if option_bag.option == option:
                            soption_bag.config_bag.unrestraint()
                            soption_bag.config_bag.remove_validation()
                            soption_bag.apply_requires = False
                        else:
                            soption_bag.config_bag.properties = soption_bag.config_bag.true_properties
                            soption_bag.config_bag.set_permissive()
                    else:
                        if not option_bag.option.impl_is_optiondescription() and option_bag.option.impl_is_follower():
                            idx = option_bag.index
                            if idx is None:
                                continue
                        is_indexed = False
                    try:
                        if not isinstance(option, tuple):
                            value = context.getattr(reqpath,
                                                    soption_bag)
                        else:
                            value = context.cfgimpl_get_values().carry_out_calculation(option_bag,
                                                                                       option[0],
                                                                                       option[1])
                    except (PropertiesOptionError, ConfigError) as err:
                        if isinstance(err, ConfigError):
                            if not isinstance(err.ori_err, PropertiesOptionError):
                                raise err
                            err = err.ori_err
                        properties = err.proptype
                        # if not transitive, properties must be verify in current requires
                        # otherwise if same_action, property must be in properties
                        # otherwise add property in returned properties (if operator is 'and')
                        if not transitive:
                            if all_properties is None:
                                all_properties = []
                                for requires_ in current_requires:
                                    for require_ in requires_:
                                        all_properties.append(require_[1])
                            if not set(properties) - set(all_properties):
                                continue
                        if same_action and action not in properties:
                            if len(properties) == 1:
                                prop_msg = _('property')
                            else:
                                prop_msg = _('properties')
                            err = RequirementError(_('cannot access to option "{0}" because '
                                                     'required option "{1}" has {2} {3}'
                                                     '').format(option_bag.option.impl_get_display_name(),
                                                                option.impl_get_display_name(),
                                                                prop_msg,
                                                                display_list(list(properties), add_quote=True)))
                            err.proptype = properties
                            raise err
                        # transitive action, add action
                        if operator != 'and':
                            if readable:
                                for msg in self.apply_requires(err._option_bag,
                                                               True).values():
                                    calc_properties.setdefault(action, []).extend(msg)
                            else:
                                calc_properties.add(action)
                                breaked = True
                                break
                    else:
                        if is_indexed:
                            value = value[option_bag.index]
                        if (not inverse and value in expected or
                                inverse and value not in expected):
                            if operator != 'and':
                                if readable:
                                    display_value = display_list(expected, 'or', add_quote=True)
                                    if isinstance(option, tuple):
                                        if not inverse:
                                            msg = _('the calculated value is {0}').format(display_value)
                                        else:
                                            msg = _('the calculated value is not {0}').format(display_value)
                                    else:
                                        name = option.impl_get_display_name()
                                        if not inverse:
                                            msg = _('the value of "{0}" is {1}').format(name, display_value)
                                        else:
                                            msg = _('the value of "{0}" is not {1}').format(name, display_value)
                                    calc_properties.setdefault(action, []).append(msg)
                                else:
                                    calc_properties.add(action)
                                    breaked = True
                                    break
                        elif operator == 'and':
                            break
                else:
                    if operator == 'and':
                        calc_properties.add(action)
                    continue
                if breaked:
                    break
        return calc_properties

    #____________________________________________________________
    # set methods
    def set_context_properties(self,
                               properties,
                               context):
        self._p_.setproperties(None,
                               properties)
        context.cfgimpl_reset_cache(None)

    def setproperties(self,
                      path,
                      properties,
                      option_bag,
                      context):
        """save properties for specified path
        (never save properties if same has option properties)
        """
        # should have index !!!
        opt = option_bag.option
        if opt.impl_getrequires() is not None:
            not_allowed_props = properties & \
                    getattr(opt, '_calc_properties', static_set)
            if not_allowed_props:
                raise ValueError(_('cannot set property {} for option "{}" this property is '
                                   'calculated').format(display_list(list(not_allowed_props),
                                                                     add_quote=True),
                                                        opt.impl_get_display_name()))
        if opt.impl_is_symlinkoption():
            raise TypeError(_("can't assign property to the symlinkoption \"{}\""
                              "").format(opt.impl_get_display_name()))
        if ('force_default_on_freeze' in properties or 'force_metaconfig_on_freeze' in properties) and \
                'frozen' not in properties and \
                opt.impl_is_leader():
            raise ConfigError(_('a leader ({0}) cannot have '
                                '"force_default_on_freeze" or "force_metaconfig_on_freeze" property without "frozen"'
                                '').format(opt.impl_get_display_name()))
        self._p_.setproperties(path,
                               properties)
        # values too because of follower values could have a PropertiesOptionError has value
        context.cfgimpl_reset_cache(option_bag)
        del option_bag.properties

    def set_context_permissives(self,
                                permissives):
        self.setpermissives(None,
                            permissives)

    def setpermissives(self,
                       option_bag,
                       permissives):
        """
        enables us to put the permissives in the storage

        :param path: the option's path
        :param type: str
        :param opt: if an option object is set, the path is extracted.
                    it is better (faster) to set the path parameter
                    instead of passing a :class:`tiramisu.option.Option()` object.
        """
        if not isinstance(permissives, frozenset):
            raise TypeError(_('permissive must be a frozenset'))
        if option_bag is not None:
            opt = option_bag.option
            if opt and opt.impl_is_symlinkoption():
                raise TypeError(_("can't assign permissive to the symlinkoption \"{}\""
                                  "").format(opt.impl_get_display_name()))
            path = option_bag.path
        else:
            path = None
        forbidden_permissives = FORBIDDEN_SET_PERMISSIVES & permissives
        if forbidden_permissives:
            raise ConfigError(_('cannot add those permissives: {0}').format(
                ' '.join(forbidden_permissives)))
        self._pp_.setpermissives(path, permissives)
        if option_bag is not None:
            option_bag.config_bag.context.cfgimpl_reset_cache(option_bag)

    #____________________________________________________________
    # reset methods

    def reset(self,
              option_bag,
              context):
        if option_bag is None:
            opt = None
            path = None
        else:
            opt = option_bag.option
            assert not opt.impl_is_symlinkoption(), _("can't reset properties to "
                                                      "the symlinkoption \"{}\""
                                                      "").format(opt.impl_get_display_name())
            path = option_bag.path
        self._p_.delproperties(path)
        context.cfgimpl_reset_cache(option_bag)

    def reset_permissives(self,
                          option_bag,
                          context):
        if option_bag is None:
            opt = None
            path = None
        else:
            opt = option_bag.option
            assert not opt.impl_is_symlinkoption(), _("can't reset permissives to "
                                                      "the symlinkoption \"{}\""
                                                      "").format(opt.impl_get_display_name())
            path = option_bag.path
        self._pp_.delpermissive(path)
        context.cfgimpl_reset_cache(option_bag)

    #____________________________________________________________
    # validate properties
    def calc_raises_properties(self,
                               option_properties,
                               config_properties,
                               config_permissives):
        properties = option_properties & config_properties - SPECIAL_PROPERTIES
        # remove global permissive properties
        if properties and ('permissive' in config_properties):
            properties -= config_permissives
        # at this point an option should not remain in properties
        return properties

    def validate_properties(self,
                            option_bag):
        """
        validation upon the properties related to `opt`

        :param opt: an option or an option description object
        :param force_permissive: behaves as if the permissive property
                                 was present
        """
        config_bag = option_bag.config_bag
        if not config_bag.properties:  # pragma: no cover
            return
        properties = self.calc_raises_properties(option_bag.properties,
                                                 config_bag.properties,
                                                 config_bag.permissives)
        if properties != frozenset():
            raise PropertiesOptionError(option_bag,
                                        properties,
                                        self)

    def validate_mandatory(self,
                           value,
                           option_bag):
        if 'mandatory' in option_bag.config_bag.properties:
            values = option_bag.config_bag.context.cfgimpl_get_values()
            is_mandatory = False
            if not ('permissive' in option_bag.config_bag.properties and
                    'mandatory' in option_bag.config_bag.permissives) and \
                    'mandatory' in option_bag.properties and values.isempty(option_bag.option,
                                                                                 value,
                                                                                 index=option_bag.index):
                is_mandatory = True
            if 'empty' in option_bag.properties and values.isempty(option_bag.option,
                                                                   value,
                                                                   force_allow_empty_list=True,
                                                                   index=option_bag.index):
                is_mandatory = True
            if is_mandatory:
                raise PropertiesOptionError(option_bag,
                                            ['mandatory'],
                                            self)

    def validate_frozen(self,
                        option_bag):
        if option_bag.config_bag.properties and \
                ('everything_frozen' in option_bag.config_bag.properties or
                 'frozen' in option_bag.properties) and \
                not (('permissive' in option_bag.config_bag.properties) and
                     'frozen' in option_bag.config_bag.permissives):
            raise PropertiesOptionError(option_bag,
                                        ['frozen'],
                                        self)
        return False
    #____________________________________________________________
    # read only/read write

    def _read(self,
              remove,
              append,
              context):
        props = self._p_.getproperties(None,
                                       self.default_properties)
        modified = False
        if remove & props:
            props = props - remove
            modified = True
        if append & props != append:
            props = props | append
            modified = True
        if modified:
            self.set_context_properties(frozenset(props),
                                        context)

    def read_only(self,
                  context):
        "convenience method to freeze, hide and disable"
        self._read(self.ro_remove,
                   self.ro_append,
                   context)

    def read_write(self,
                   context):
        "convenience method to freeze, hide and disable"
        self._read(self.rw_remove,
                   self.rw_append,
                   context)
