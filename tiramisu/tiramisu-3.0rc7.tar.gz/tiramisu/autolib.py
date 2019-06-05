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
# the rough gus of pypy: pypy: http://codespeak.net/svn/pypy/dist/pypy/config/
# the whole pypy projet is under MIT licence
# ____________________________________________________________
"enables us to carry out a calculation and return an option's value"
from typing import Any, Optional, Union, Callable, Dict, List


from .error import PropertiesOptionError, ConfigError, LeadershipError
from .i18n import _
from .setting import undefined, ConfigBag, OptionBag, Undefined
from .storage import get_default_values_storages, get_default_settings_storages
from .function import ParamValue, ParamContext, ParamIndex, ParamOption, Params
# ____________________________________________________________


def manager_callback(callbk: Union[ParamOption, ParamValue],
                     option,
                     index: Optional[int],
                     orig_value,
                     config_bag: ConfigBag,
                     fromconsistency: List) -> Any:
    """replace Param by true value"""
    if isinstance(callbk, ParamValue):
        return callbk.value
    if isinstance(callbk, ParamIndex):
        return index
    if config_bag is undefined:
        return undefined
    if isinstance(callbk, ParamContext):
        #Not an option, set full context
        return config_bag.context.duplicate(force_values=get_default_values_storages(),
                                            force_settings=get_default_settings_storages())
    opt = callbk.option
    if opt.issubdyn():
        opt = opt.to_dynoption(option.rootpath,
                               option.impl_getsuffix())
    path = opt.impl_getpath()
    if index is not None and opt.impl_get_leadership() and \
            opt.impl_get_leadership().in_same_group(option):
        if opt == option:
            index_ = None
            with_index = False
        elif opt.impl_is_follower():
            index_ = index
            with_index = False
        else:
            index_ = None
            with_index = True
    else:
        index_ = None
        with_index = False
    if opt == option and orig_value is not undefined and \
            (not opt.impl_is_follower() or index is None):
        return orig_value
    # don't validate if option is option that we tried to validate
    config_bag = config_bag.copy()
    config_bag.set_permissive()
    config_bag.properties -= {'warnings'}
    option_bag = OptionBag()
    option_bag.set_option(opt,
                          path,
                          index_,
                          config_bag)
    if fromconsistency:
        option_bag.fromconsistency = fromconsistency.copy()
    if opt == option:
        option_bag.config_bag.unrestraint()
        option_bag.config_bag.remove_validation()
    try:
        # get value
        value = config_bag.context.getattr(path,
                                           option_bag)
        if with_index:
            return value[index]
        return value
    except PropertiesOptionError as err:
        # raise PropertiesOptionError (which is catched) because must not add value None in carry_out_calculation
        if callbk.notraisepropertyerror:
            raise err
        raise ConfigError(_('unable to carry out a calculation for "{}"'
                            ', {}').format(option.impl_get_display_name(), err), err)


def carry_out_calculation(option,
                          callback: Callable,
                          callback_params: Optional[Params],
                          index: Optional[int],
                          config_bag: Optional[ConfigBag],
                          fromconsistency: List,
                          orig_value=undefined,
                          is_validator: int=False):

    """a function that carries out a calculation for an option's value

    :param option: the option
    :param callback: the name of the callback function
    :type callback: str
    :param callback_params: the callback's parameters
                            (only keyword parameters are allowed)
    :type callback_params: dict
    :param index: if an option is multi, only calculates the nth value
    :type index: int
    :param is_validator: to know if carry_out_calculation is used to validate a value

    The callback_params is a dict. Key is used to build args (if key is '')
    and kwargs (otherwise). Values are tuple of:
    - values
    - tuple with option and boolean's force_permissive (True when don't raise
    if PropertiesOptionError)
    Values could have multiple values only when key is ''.

    * if no callback_params:
      => calculate(<function func at 0x2092320>, [], {})

    * if callback_params={'': ('yes',)}
      => calculate(<function func at 0x2092320>, ['yes'], {})

    * if callback_params={'value': ('yes',)}
      => calculate(<function func at 0x165b320>, [], {'value': 'yes'})

    * if callback_params={'': ('yes', 'no')}
      => calculate('yes', 'no')

    * if callback_params={'value': ('yes', 'no')}
      => ValueError()

    * if callback_params={'': (['yes', 'no'],)}
      => calculate(<function func at 0x176b320>, ['yes', 'no'], {})

    * if callback_params={'value': ('yes', 'no')}
      => raises ValueError()

    * if callback_params={'': ((opt1, False),)}

       - a simple option:
         opt1 == 11
         => calculate(<function func at 0x1cea320>, [11], {})

       - a multi option and not leadership
         opt1 == [1, 2, 3]
         => calculate(<function func at 0x223c320>, [[1, 2, 3]], {})

       - option is leader or follower of opt1:
         opt1 == [1, 2, 3]
         => calculate(<function func at 0x223c320>, [1], {})
         => calculate(<function func at 0x223c320>, [2], {})
         => calculate(<function func at 0x223c320>, [3], {})

      - opt is a leader or follower but not related to option:
        opt1 == [1, 2, 3]
        => calculate(<function func at 0x11b0320>, [[1, 2, 3]], {})

    * if callback_params={'value': ((opt1, False),)}

       - a simple option:
         opt1 == 11
         => calculate(<function func at 0x17ff320>, [], {'value': 11})

       - a multi option:
         opt1 == [1, 2, 3]
         => calculate(<function func at 0x1262320>, [], {'value': [1, 2, 3]})

    * if callback_params={'': ((opt1, False), (opt2, False))}

      - two single options
          opt1 = 11
          opt2 = 12
          => calculate(<function func at 0x217a320>, [11, 12], {})

      - a multi option with a simple option
          opt1 == [1, 2, 3]
          opt2 == 12
          => calculate(<function func at 0x2153320>, [[1, 2, 3], 12], {})

      - a multi option with an other multi option but with same length
          opt1 == [1, 2, 3]
          opt2 == [11, 12, 13]
          => calculate(<function func at 0x1981320>, [[1, 2, 3], [11, 12, 13]], {})

      - a multi option with an other multi option but with different length
          opt1 == [1, 2, 3]
          opt2 == [11, 12]
          => calculate(<function func at 0x2384320>, [[1, 2, 3], [11, 12]], {})

      - a multi option without value with a simple option
          opt1 == []
          opt2 == 11
          => calculate(<function func at 0xb65320>, [[], 12], {})

    * if callback_params={'value': ((opt1, False), (opt2, False))}
      => raises ValueError()

    If index is not undefined, return a value, otherwise return:

    * a list if one parameters have multi option
    * a value otherwise

    If calculate return list, this list is extend to return value.
    """
    args = []
    kwargs = {}
    # if callback_params has a callback, launch several time calculate()
    if option.issubdyn():
        #FIXME why here? should be a ParamSuffix !
        kwargs['suffix'] = option.impl_getsuffix()
    if callback_params:
        for callbk in callback_params.args:
            try:
                value = manager_callback(callbk,
                                         option,
                                         index,
                                         orig_value,
                                         config_bag,
                                         fromconsistency)
                if value is undefined:
                    return undefined
                args.append(value)
            except PropertiesOptionError:
                pass
        for key, callbk in callback_params.kwargs.items():
            try:
                value = manager_callback(callbk,
                                         option,
                                         index,
                                         orig_value,
                                         config_bag,
                                         fromconsistency)
                if value is undefined:
                    return undefined
                kwargs[key] = value
            except PropertiesOptionError:
                pass
    ret = calculate(option,
                    callback,
                    is_validator,
                    args,
                    kwargs)
    if isinstance(ret, list) and not option.impl_is_dynoptiondescription() and \
            option.impl_is_follower():
        if args or kwargs:
            raise LeadershipError(_('function "{}" with arguments "{}" and "{}" '
                                    'return the list "{}" for the follower option "{}"'
                                    '').format(callback.__name__,
                                               args,
                                               kwargs,
                                               ret,
                                               option.impl_get_display_name()))
        else:
            raise LeadershipError(_('function "{}" return the list "{}" for the follower option "{}"'
                                    '').format(callback.__name__,
                                               ret,
                                               option.impl_getname()))
    return ret


def calculate(option,
              callback: Callable,
              is_validator: bool,
              args,
              kwargs):
    """wrapper that launches the 'callback'

    :param callback: callback function
    :param args: in the callback's arity, the unnamed parameters
    :param kwargs: in the callback's arity, the named parameters

    """
    try:
        return callback(*args, **kwargs)
    except ValueError as err:
        if is_validator:
            raise err
        error = err
    except Exception as err:
        error = err
    if args or kwargs:
        msg = _('unexpected error "{0}" in function "{1}" with arguments "{3}" and "{4}" '
                'for option "{2}"').format(str(error),
                                           callback.__name__,
                                           option.impl_get_display_name(),
                                           args,
                                           kwargs)
    else:
        msg = _('unexpected error "{0}" in function "{1}" for option "{2}"'
                '').format(str(error),
                           callback.__name__,
                           option.impl_get_display_name())
    del error
    raise ConfigError(msg)
