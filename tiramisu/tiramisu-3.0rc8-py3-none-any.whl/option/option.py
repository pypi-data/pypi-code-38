# -*- coding: utf-8 -*-
"option types and option description"
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
import warnings
import weakref
from typing import Any, List, Callable, Optional, Dict, Union, Tuple

from .baseoption import BaseOption, submulti, STATIC_TUPLE
from ..i18n import _
from ..setting import undefined, OptionBag, Undefined
from ..autolib import carry_out_calculation
from ..error import (ConfigError, ValueWarning, ValueErrorWarning, PropertiesOptionError,
                     ValueOptionError, display_list)
from ..function import Params, ParamValue
from .syndynoption import SynDynOption
ALLOWED_CONST_LIST = ['_cons_not_equal']


class Option(BaseOption):
    """
    Abstract base class for configuration option's.

    Reminder: an Option object is **not** a container for the value.
    """
    __slots__ = ('_extra',
                 '_warnings_only',
                 '_allow_empty_list',
                 #multi
                 '_multi',
                 '_unique',
                 #value
                 '_default',
                 '_default_multi',
                 #calcul
                 '_val_call',
                 #
                 '_leadership',
                 '_choice_values',
                 '_choice_values_params',
                )
    _empty = ''
    def __init__(self,
                 name: str,
                 doc: str,
                 default: Any=undefined,
                 default_multi: Any=None,
                 requires: List[Dict]=None,
                 multi: bool=False,
                 unique: bool=undefined,
                 callback: Optional[Callable]=None,
                 callback_params: Optional[Params]=None,
                 validator: Optional[Callable]=None,
                 validator_params: Optional[Params]=None,
                 properties: Optional[List[str]]=None,
                 warnings_only: bool=False,
                 extra: Optional[Dict]=None,
                 allow_empty_list: bool=undefined) -> None:
        _setattr = object.__setattr__
        if not multi and default_multi is not None:
            raise ValueError(_("default_multi is set whereas multi is False"
                               " in option: {0}").format(name))
        if default is undefined:
            if multi is False:
                default = None
            else:
                default = []
        if multi is True:
            is_multi = True
            _multi = 0
        elif multi is False:
            is_multi = False
            _multi = 1
        elif multi is submulti:
            is_multi = True
            _multi = submulti
        else:
            raise ValueError(_('invalid multi type "{}"').format(multi))
        if _multi != 1:
            _setattr(self, '_multi', _multi)
        if multi is not False and default is None:
            default = []
        super().__init__(name,
                         doc,
                         requires=requires,
                         properties=properties,
                         is_multi=is_multi)
        if validator is not None:
            validator_params = self._build_calculator_params(validator,
                                                             validator_params,
                                                             'validator',
                                                             add_value=True)
            if not validator_params:
                val_call = (validator,)
            else:
                val_call = (validator, validator_params)
            self._val_call = (val_call, None)
        if extra is not None and extra != {}:
            _setattr(self, '_extra', extra)
        if unique != undefined and not isinstance(unique, bool):
            raise ValueError(_('unique must be a boolean, not "{}"').format(unique))
        if not is_multi and unique is True:
            raise ValueError(_('unique must be set only with multi value'))
        if warnings_only is True:
            _setattr(self, '_warnings_only', warnings_only)
        if allow_empty_list is not undefined:
            _setattr(self, '_allow_empty_list', allow_empty_list)
        if is_multi and default_multi is not None:
            def test_multi_value(value):
                try:
                    self._validate(value,
                                   undefined)
                except ValueError as err:
                    raise ValueError(_("invalid default_multi value {0} "
                                       "for option {1}: {2}").format(str(value),
                                                                     self.impl_getname(),
                                                                     str(err)))
            if _multi is submulti:
                if not isinstance(default_multi, list):
                    raise ValueError(_('invalid default_multi value "{0}" '
                                       'for option "{1}", must be a list for a submulti'
                                       '').format(str(default_multi),
                                                 self.impl_get_display_name()))
                for value in default_multi:
                    test_multi_value(value)
            else:
                test_multi_value(default_multi)
            _setattr(self, '_default_multi', default_multi)
        if unique is not undefined:
            _setattr(self, '_unique', unique)
        option_bag = OptionBag()
        option_bag.set_option(self,
                              undefined,
                              None,
                              undefined)
        self.impl_validate(default,
                           option_bag)
        if (is_multi and default != []) or \
                (not is_multi and default is not None):
            if is_multi:
                default = tuple(default)
            _setattr(self, '_default', default)

        self._impl_set_callback(callback,
                                callback_params)

    #__________________________________________________________________________
    # option's information

    def impl_is_multi(self) -> bool:
        return getattr(self, '_multi', 1) != 1

    def impl_is_submulti(self) -> bool:
        return getattr(self, '_multi', 1) == 2

    def impl_is_unique(self) -> bool:
        return getattr(self, '_unique', False)

    def impl_allow_empty_list(self) -> Union[Undefined, bool]:
        return getattr(self, '_allow_empty_list', undefined)

    def impl_is_dynsymlinkoption(self) -> bool:
        return False

    def get_type(self) -> str:
        # _display_name for compatibility with older version than 3.0rc3
        return getattr(self, '_type', self._display_name)

    def get_display_type(self) -> str:
        return self._display_name

    def impl_getdefault(self) -> Any:
        "accessing the default value"
        is_multi = self.impl_is_multi()
        default = getattr(self, '_default', undefined)
        if default is undefined:
            if is_multi:
                default = []
            else:
                default = None
        else:
            if is_multi:
                default = list(default)
        return default

    def impl_getdefault_multi(self) -> Any:
        "accessing the default value for a multi"
        if self.impl_is_submulti():
            default_value = []
        else:
            default_value = None
        return getattr(self, '_default_multi', default_value)

    def impl_get_extra(self,
                       key: str) -> Any:
        extra = getattr(self, '_extra', {})
        if isinstance(extra, tuple):
            if key in extra[0]:
                return extra[1][extra[0].index(key)]
            return None
        else:
            return extra.get(key)

    #__________________________________________________________________________
    # validator

    def impl_get_validator(self) -> Tuple[Callable, Params]:
        val = getattr(self, '_val_call', (None,))[0]
        if val is None:
            ret_val = (None, None)
        elif len(val) == 1:
            ret_val = (val[0], None)
        else:
            ret_val = val
        return ret_val

    def impl_validate(self,
                      value: Any,
                      option_bag: OptionBag,
                      check_error: bool=True) -> None:
        """
        """
        config_bag = option_bag.config_bag
        force_index = option_bag.index
        is_warnings_only = getattr(self, '_warnings_only', False)

        if check_error and config_bag is not undefined and \
                not 'validator' in config_bag.properties:
            # just to check propertieserror
            self.valid_consistency(option_bag,
                                   value,
                                   check_error,
                                   is_warnings_only)
            return

        def _is_not_unique(value):
            # if set(value) has not same length than value
            if check_error and self.impl_is_unique() and \
                    len(set(value)) != len(value):
                for idx, val in enumerate(value):
                    if val in value[idx+1:]:
                        raise ValueError(_('invalid value "{}", this value is already in "{}"'
                                           '').format(val,
                                                      self.impl_get_display_name()))

        def calculation_validator(val,
                                  _index):
            validator, validator_params = self.impl_get_validator()
            if validator is not None:
                #inject value in calculation
                if validator_params is None:
                    args = []
                    kwargs = None
                else:
                    args = list(validator_params.args)
                    kwargs = validator_params.kwargs
                args.insert(0, ParamValue(val))
                validator_params_ = Params(tuple(args), kwargs)
                # Raise ValueError if not valid
                carry_out_calculation(option_bag.ori_option,
                                      callback=validator,
                                      callback_params=validator_params_,
                                      index=_index,
                                      config_bag=option_bag.config_bag,
                                      fromconsistency=option_bag.fromconsistency,
                                      orig_value=value,
                                      is_validator=True)

        def do_validation(_value,
                          _index):
            if isinstance(_value, list):
                raise ValueError(_('which must not be a list').format(_value,
                                                                      self.impl_get_display_name()))
            if _value is not None:
                if check_error:
                    # option validation
                    self._validate(_value,
                                   option_bag,
                                   option_bag.ori_option)
                if ((check_error and not is_warnings_only) or
                        (not check_error and is_warnings_only)):
                    try:
                        calculation_validator(_value,
                                              _index)
                        self._second_level_validation(_value,
                                                      is_warnings_only)
                    except ValueError as err:
                        if is_warnings_only:
                            warnings.warn_explicit(ValueWarning(_value,
                                                                self._display_name,
                                                                self,
                                                                '{0}'.format(err),
                                                                _index),
                                                   ValueWarning,
                                                   self.__class__.__name__, 0)
                        else:
                            raise err
        try:
            val = value
            err_index = force_index
            if not self.impl_is_multi():
                do_validation(val, None)
            elif force_index is not None:
                if self.impl_is_submulti():
                    if not isinstance(value, list):
                        raise ValueError(_('which must be a list'))
                    _is_not_unique(value)
                    for val in value:
                        do_validation(val,
                                      force_index)
                else:
                    do_validation(val,
                                  force_index)
            elif not isinstance(value, list):
                raise ValueError(_('which must be a list'))
            elif self.impl_is_submulti():
                for err_index, lval in enumerate(value):
                    _is_not_unique(lval)
                    if not isinstance(lval, list):
                        raise ValueError(_('which "{}" must be a list of list'
                                           '').format(lval))
                    for val in lval:
                        do_validation(val,
                                      err_index)
            else:
                _is_not_unique(value)
                for err_index, val in enumerate(value):
                    do_validation(val,
                                  err_index)

            if not is_warnings_only or not check_error:
                self.valid_consistency(option_bag,
                                       value,
                                       check_error,
                                       is_warnings_only)
        except ValueError as err:
            if config_bag is undefined or \
                    'demoting_error_warning' not in config_bag.properties:
                raise ValueOptionError(val,
                                       self._display_name,
                                       option_bag.ori_option,
                                       '{0}'.format(err),
                                       err_index)
            warnings.warn_explicit(ValueErrorWarning(val,
                                                    self._display_name,
                                                    option_bag.ori_option,
                                                    '{0}'.format(err),
                                                    err_index),
                                   ValueErrorWarning,
                                   self.__class__.__name__, 0)

    def _validate_calculator(self,
                            callback: Callable,
                            callback_params: Optional[Params]=None) -> None:
        if callback is None:
            return
        default_multi = getattr(self, '_default_multi', None)
        is_multi = self.impl_is_multi()
        default = self.impl_getdefault()
        if (not is_multi and (default is not None or default_multi is not None)) or \
                (is_multi and (default != [] or default_multi is not None)):
            raise ValueError(_('default value not allowed if option "{0}" '
                             'is calculated').format(self.impl_getname()))

    def _second_level_validation(self,
                                 value: Any,
                                 warnings_only: bool) -> None:
        pass

    #__________________________________________________________________________
    # leadership
    # def impl_is_leadership(self):
    #     return self.impl_get_leadership() is not None

    def impl_is_leader(self):
        leadership = self.impl_get_leadership()
        if leadership is None:
            return False
        return leadership.is_leader(self)

    def impl_is_follower(self):
        leadership = self.impl_get_leadership()
        if leadership is None:
            return False
        return not leadership.is_leader(self)

    def impl_get_leadership(self):
        leadership = getattr(self, '_leadership', None)
        if leadership is None:
            return leadership
        return leadership()

    #____________________________________________________________
    # consistencies

    def impl_add_consistency(self,
                             func: str,
                             *other_opts,
                             **params) -> None:
        """Add consistency means that value will be validate with other_opts
        option's values.

        :param func: function's name
        :type func: `str`
        :param other_opts: options used to validate value
        :type other_opts: `list` of `tiramisu.option.Option`
        :param params: extra params (warnings_only and transitive are allowed)
        """
        if self.impl_is_readonly():
            raise AttributeError(_("'{0}' ({1}) cannot add consistency, option is"
                                   " read-only").format(
                                       self.__class__.__name__,
                                       self.impl_getname()))
        self._valid_consistencies(other_opts,
                                  func=func)
        func = '_cons_{0}'.format(func)
        if func not in dir(self):
            raise ConfigError(_('consistency {0} not available for this option').format(func))
        options = [weakref.ref(self)]
        for option in other_opts:
            options.append(weakref.ref(option))
        all_cons_opts = tuple(options)
        unknown_params = set(params.keys()) - set(['warnings_only', 'transitive'])
        if unknown_params != set():
            raise ValueError(_('unknown parameter {0} in consistency').format(unknown_params))
        self._add_consistency(func,
                              all_cons_opts,
                              params)
        #validate default value when add consistency
        option_bag = OptionBag()
        option_bag.set_option(self,
                              undefined,
                              None,
                              undefined)
        self.impl_validate(self.impl_getdefault(),
                           option_bag)
        self.impl_validate(self.impl_getdefault(),
                           option_bag,
                           check_error=False)
        if func != '_cons_not_equal':
            #consistency could generate warnings or errors
            self._has_dependency = True
        for wopt in all_cons_opts:
            opt = wopt()
            if func in ALLOWED_CONST_LIST:
                if getattr(opt, '_unique', undefined) == undefined:
                    opt._unique = True
            if opt != self:
                self._add_dependency(opt)
                opt._add_dependency(self)

    def _add_consistency(self,
                         func: str,
                         all_cons_opts: List[BaseOption],
                         params: Dict) -> None:
        cons = (-1, func, all_cons_opts, params)
        consistencies = getattr(self, '_consistencies', None)
        if consistencies is None:
            self._consistencies = [cons]
        else:
            consistencies.append(cons)

    def get_consistencies(self):
        return getattr(self, '_consistencies', STATIC_TUPLE)

    def has_consistencies(self, context) -> bool:
        descr = context.cfgimpl_get_description()
        if getattr(descr, '_cache_consistencies', None) is None:
            return False
        return self in descr._cache_consistencies

    def valid_consistency(self,
                          option_bag: OptionBag,
                          value: Any,
                          check_error: bool,
                          option_warnings_only: bool) -> None:
        if option_bag.config_bag is not undefined:
            descr = option_bag.config_bag.context.cfgimpl_get_description()
            # no consistency found at all
            if getattr(descr, '_cache_consistencies', None) is None:
                return
            # get consistencies for this option
            consistencies = descr._cache_consistencies.get(option_bag.option)
        else:
            # is no context, get consistencies in option
            consistencies = option_bag.option.get_consistencies()
        if consistencies:
            if option_bag.config_bag is undefined:
                coption_bag = option_bag.copy()
            else:
                cconfig_bag = option_bag.config_bag.copy()
                cconfig_bag.remove_warnings()
                cconfig_bag.set_permissive()
                coption_bag = option_bag.copy()
                coption_bag.config_bag = cconfig_bag
            if not option_bag.fromconsistency:
                fromconsistency_is_empty = True
                option_bag.fromconsistency = [cons_id for cons_id, f, a, p in consistencies]
            else:
                fromconsistency_is_empty = False
            for cons_id, func, all_cons_opts, params in consistencies:
                if not fromconsistency_is_empty and cons_id in option_bag.fromconsistency:
                    continue
                warnings_only = option_warnings_only or params.get('warnings_only', False)
                if (warnings_only and not check_error) or (not warnings_only and check_error):
                    transitive = params.get('transitive', True)
                    #all_cons_opts[0] is the option where func is set
                    if option_bag.ori_option.impl_is_dynsymlinkoption():
                        opts = []
                        for opt in all_cons_opts:
                            opts.append(opt().to_dynoption(option_bag.ori_option.rootpath,
                                                           option_bag.ori_option.suffix))
                        wopt = opts[0]
                    else:
                        opts = all_cons_opts
                        wopt = opts[0]()
                    wopt.launch_consistency(self,
                                            func,
                                            cons_id,
                                            coption_bag,
                                            value,
                                            opts,
                                            warnings_only,
                                            transitive)
            if fromconsistency_is_empty:
                option_bag.fromconsistency = []

    def _valid_consistencies(self,
                             other_opts: List[BaseOption],
                             init: bool=True,
                             func: Optional[str]=None) -> None:
        if self.issubdyn():
            dynod = self.getsubdyn()
        else:
            dynod = None
        if self.impl_is_submulti():
            raise ConfigError(_('cannot add consistency with submulti option'))
        is_multi = self.impl_is_multi()
        for opt in other_opts:
            if isinstance(opt, weakref.ReferenceType):
                opt = opt()
            assert not opt.impl_is_submulti(), _('cannot add consistency with submulti option')
            assert isinstance(opt, Option), _('consistency must be set with an option, not {}').format(opt)
            if opt.issubdyn():
                if dynod is None:
                    raise ConfigError(_('almost one option in consistency is '
                                        'in a dynoptiondescription but not all'))
                subod = opt.getsubdyn()
                if dynod != subod:
                    raise ConfigError(_('option in consistency must be in same'
                                        ' dynoptiondescription'))
                dynod = subod
            elif dynod is not None:
                raise ConfigError(_('almost one option in consistency is in a '
                                    'dynoptiondescription but not all'))
            if self is opt:
                raise ConfigError(_('cannot add consistency with itself'))
            if is_multi != opt.impl_is_multi():
                raise ConfigError(_('every options in consistency must be '
                                    'multi or none'))
            # FIXME
            if init and func != 'not_equal':
                opt._has_dependency = True

    def launch_consistency(self,
                           current_opt: BaseOption,
                           func: Callable,
                           cons_id: int,
                           option_bag: OptionBag,
                           value: Any,
                           opts: List[BaseOption],
                           warnings_only: bool,
                           transitive: bool) -> None:
        """Launch consistency now
        """
        all_cons_vals = []
        all_cons_opts = []
        length = None
        for opt in opts:
            if isinstance(opt, weakref.ReferenceType):
                opt = opt()
            try:
                opt_value = self.get_consistency_value(option_bag,
                                                       opt,
                                                       cons_id,
                                                       value,
                                                       func)
            except PropertiesOptionError as err:
                if transitive:
                    err.set_orig_opt(option_bag.option)
                    raise err
            else:
                if opt.impl_is_multi() and option_bag.index is None and \
                        func not in ALLOWED_CONST_LIST:
                    len_value = len(opt_value)
                    if length is not None and length != len_value:
                        if option_bag.config_bag is undefined:
                            return
                        raise ValueError(_('unexpected length of "{}" in constency "{}", '
                                           'should be "{}"').format(len(opt_value),
                                                                    opt.impl_get_display_name(),
                                                                    length))  # pragma: no cover
                    length = len_value
                if isinstance(opt_value, list) and func in ALLOWED_CONST_LIST:
                    for value_ in opt_value:
                        all_cons_vals.append(value_)
                        all_cons_opts.append(opt)
                else:
                    all_cons_vals.append(opt_value)
                    all_cons_opts.append(opt)
        if option_bag.config_bag is not undefined and \
                not 'validator' in option_bag.config_bag.properties:
            return
        all_values = []
        if length is None:
            all_values = [all_cons_vals]
        elif length:
            all_values = zip(*all_cons_vals)
        try:
            context = option_bag.config_bag if option_bag.config_bag is undefined else option_bag.config_bag.context
            for values in all_values:
                getattr(self, func)(current_opt,
                                    all_cons_opts,
                                    values,
                                    warnings_only,
                                    context)
        except ValueError as err:
            if warnings_only:
                warnings.warn_explicit(ValueWarning(value,
                                                    self._display_name,
                                                    current_opt,
                                                    "{}".format(err),
                                                    option_bag.index),
                                       ValueWarning,
                                       self.__class__.__name__, 0)
            else:
                raise err

    def get_consistency_value(self,
                              option_bag: OptionBag,
                              current_option: BaseOption,
                              cons_id: int,
                              value: Any,
                              func: str) -> Any:
        if option_bag.ori_option == current_option:
            # orig_option is current option
            # we have already value, so use it
            return value
        if option_bag.config_bag is undefined:
            #if no context get default value
            return current_option.impl_getdefault()
        if func in ALLOWED_CONST_LIST:
            index = None
            index_ = None
        elif current_option.impl_is_leader():
            index = option_bag.index
            index_ = None
        else:
            index = option_bag.index
            index_ = index
        #otherwise calculate value
        path = current_option.impl_getpath()
        coption_bag = OptionBag()
        coption_bag.set_option(current_option,
                               path,
                               index_,
                               option_bag.config_bag)
        fromconsistency = option_bag.fromconsistency.copy()
        fromconsistency.append(cons_id)
        coption_bag.fromconsistency = fromconsistency
        current_value = option_bag.config_bag.context.getattr(path,
                                                              coption_bag)
        if index_ is None and index is not None:
            #if self is a follower and current_option is a leader and func not in ALLOWED_CONST_LIST
            #return only the value of the leader for isolate follower
            current_value = current_value[index]
        return current_value

    def _cons_not_equal(self,
                        current_opt: BaseOption,
                        opts: List[BaseOption],
                        vals: List[Any],
                        warnings_only: bool,
                        context) -> None:
        equal = []
        is_current = False
        for idx_inf, val_inf in enumerate(vals):
            for idx_sup, val_sup in enumerate(vals[idx_inf + 1:]):
                if val_inf == val_sup is not None:
                    for opt_ in [opts[idx_inf], opts[idx_inf + idx_sup + 1]]:
                        if opt_ == current_opt:
                            is_current = True
                        else:
                            if opt_ not in equal:
                                equal.append(opt_)
        if equal:
            if is_current:
                if warnings_only:
                    msg = _('should be different from the value of {}')
                else:
                    msg = _('must be different from the value of {}')
            else:
                if warnings_only:
                    msg = _('value for {} should be different')
                else:
                    msg = _('value for {} must be different')
            equal_name = []
            for opt in equal:
                equal_name.append(opt.impl_get_display_name())
            raise ValueError(msg.format(display_list(list(equal_name), add_quote=True)))

    def to_dynoption(self,
                     rootpath: str,
                     suffix: str) -> SynDynOption:
        return SynDynOption(self,
                            rootpath,
                            suffix)
