# -*- coding: utf-8 -*-
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
from types import FunctionType
from typing import FrozenSet, Callable, Tuple, Set, Optional, Union, Any, List
import weakref
from inspect import signature
from itertools import chain


from ..i18n import _
from ..setting import undefined, Settings
from ..value import Values
from ..error import ConfigError, display_list
from ..function import Params, ParamContext, ParamOption, ParamIndex

STATIC_TUPLE = frozenset()


submulti = 2


def valid_name(name):
    if not isinstance(name, str):
        return False
    return True


#____________________________________________________________
#
class Base:
    """Base use by all *Option* classes (Option, OptionDescription, SymLinkOption, ...)
    """
    __slots__ = ('_name',
                 '_path',
                 '_informations',
                 #calcul
                 '_subdyn',
                 '_requires',
                 '_properties',
                 '_calc_properties',
                 #
                 '_consistencies',
                 #other
                 '_has_dependency',
                 '_dependencies',
                 '_has_calc_context',
                 '__weakref__'
                )

    def __init__(self,
                 name: str,
                 doc: str,
                 requires=None,
                 properties=None,
                 is_multi: bool=False) -> None:
        if not valid_name(name):
            raise ValueError(_('"{0}" is an invalid name for an option').format(name))
        if requires is not None:
            calc_properties, requires = validate_requires_arg(self,
                                                              is_multi,
                                                              requires,
                                                              name)
        else:
            calc_properties = frozenset()
            requires = undefined
        if properties is None:
            properties = frozenset()
        if isinstance(properties, tuple):
            properties = frozenset(properties)
        if is_multi and 'empty' not in properties:
            # if option is a multi, it cannot be "empty" (None not allowed in the list)
            # "empty" is removed for follower's option
            properties = properties | {'empty'}
        if not isinstance(properties, frozenset):
            raise TypeError(_('invalid properties type {0} for {1},'
                              ' must be a frozenset').format(type(properties),
                                                         name))
        self.validate_properties(name,
                                 calc_properties,
                                 properties)
        _setattr = object.__setattr__
        _setattr(self, '_name', name)
        _setattr(self, '_informations', {'doc': doc})
        if calc_properties is not undefined:
            _setattr(self, '_calc_properties', calc_properties)
        if requires is not undefined:
            _setattr(self, '_requires', requires)
        if properties:
            _setattr(self, '_properties', properties)

    def validate_properties(self,
                            name: str,
                            calc_properties: FrozenSet[str],
                            properties: FrozenSet[str]) -> None:
        set_forbidden_properties = calc_properties & properties
        if set_forbidden_properties != frozenset():
            raise ValueError(_('conflict: properties already set in requirement {0} for {1}'
                               '').format(display_list(set_forbidden_properties, add_quote=True),
                                          name))

    def _get_function_args(self,
                           function: Callable) -> Tuple[Set[str], Set[str], bool, bool]:
        args = set()
        kwargs = set()
        positional = False
        keyword = False
        for param in signature(function).parameters.values():
            if param.kind == param.VAR_POSITIONAL:
                positional = True
            elif param.kind == param.VAR_KEYWORD:
                keyword = True
            elif param.default is param.empty:
                args.add(param.name)
            else:
                kwargs.add(param.name)
        return args, kwargs, positional, keyword

    def _get_parameters_args(self,
                             calculator_params: Optional[Params],
                             add_value: bool) -> Tuple[Set[str], Set[str]]:
        args = set()
        kwargs = set()
        # add value as first argument
        if add_value:
            args.add('value')
        if self.impl_is_dynoptiondescription():
            kwargs.add('suffix')
        if calculator_params:
            for idx in range(len(calculator_params.args)):
                # construct an appropriate name
                args.add('param{}'.format(idx))
            for param in calculator_params.kwargs:
                kwargs.add(param)
        return args, kwargs

    def _build_calculator_params(self,
                                 calculator: Callable,
                                 calculator_params: Optional[Params],
                                 type_: str,
                                 add_value: bool=False) -> Union[None, Params]:
        """
        :add_value: add value as first argument for validator
        """
        assert isinstance(calculator, FunctionType), _('{0} must be a function').format(type_)
        if calculator_params is not None:
            assert isinstance(calculator_params, Params), _('{0}_params must be a params'
                                                            '').format(type_)
            for param in chain(calculator_params.args, calculator_params.kwargs.values()):
                if isinstance(param, ParamContext):
                    self._has_calc_context = True
                elif isinstance(param, ParamOption):
                    param.option._add_dependency(self)
                    if type_ == 'validator':
                        self._has_dependency = True
        is_multi = self.impl_is_optiondescription() or self.impl_is_multi()
        func_args, func_kwargs, func_positional, func_keyword = self._get_function_args(calculator)
        calculator_args, calculator_kwargs = self._get_parameters_args(calculator_params, add_value)
        # remove knowned kwargs
        common_kwargs = func_kwargs & calculator_kwargs
        func_kwargs -= common_kwargs
        calculator_kwargs -= common_kwargs
        # remove knowned calculator's kwargs in func's args
        common = func_args & calculator_kwargs
        func_args -= common
        calculator_kwargs -= common
        # remove unknown calculator's args in func's args
        for idx in range(min(len(calculator_args), len(func_args))):
            func_args.pop()
            calculator_args.pop()
        # remove unknown calculator's args in func's kwargs
        if is_multi:
            func_kwargs_left = func_kwargs - {'index', 'self'}
        else:
            func_kwargs_left = func_kwargs
        func_kwargs_pop = set()
        for idx in range(min(len(calculator_args), len(func_kwargs_left))):
            func_kwargs_pop.add(func_kwargs_left.pop())
            calculator_args.pop()
        func_kwargs -= func_kwargs_pop
        # func_positional or keyword is True, so assume all args or kwargs are satisfy
        if func_positional:
            calculator_args = set()
        if func_keyword:
            calculator_kwargs = set()
        if calculator_args or calculator_kwargs:
            # there is more args/kwargs than expected!
            raise ConfigError(_('cannot find those arguments "{}" in function "{}" for "{}"'
                                '').format(display_list(list(calculator_args | calculator_kwargs)),
                                           calculator.__name__,
                                           self.impl_get_display_name()))
        has_index = False
        if is_multi and func_args and not self.impl_is_dynoptiondescription():
            if calculator_params is None:
                calculator_params = Params()
            params = list(calculator_params.args)
            if add_value:
                # only for validator
                params.append(ParamOption(self))
                func_args.pop()
            if func_args:
                has_index = True
                params.append(ParamIndex())
                func_args.pop()
            calculator_params.args = tuple(params)
        if func_args:
            raise ConfigError(_('missing those arguments "{}" in function "{}" for "{}"'
                                '').format(display_list(list(func_args)),
                                           calculator.__name__,
                                           self.impl_get_display_name()))
        if not self.impl_is_dynoptiondescription() and is_multi and \
                not has_index and 'index' in func_kwargs:
            calculator_params.kwargs['index'] = ParamIndex()
        return calculator_params

    def impl_has_dependency(self,
                            self_is_dep: bool=True) -> bool:
        if self_is_dep is True:
            return getattr(self, '_has_dependency', False)
        return hasattr(self, '_dependencies')

    def _get_dependencies(self,
                          context_od) -> Set[str]:
        ret = set(getattr(self, '_dependencies', STATIC_TUPLE))
        if context_od and hasattr(context_od, '_dependencies'):
            # if context is set in options, add those options
            return set(context_od._dependencies) | ret
        return ret

    def _add_dependency(self,
                        option) -> None:
        options = self._get_dependencies(None)
        options.add(weakref.ref(option))
        self._dependencies = tuple(options)

    def _impl_set_callback(self,
                           callback: Callable,
                           callback_params: Optional[Params]=None) -> None:
        if __debug__:
            if callback is None and callback_params is not None:
                raise ValueError(_("params defined for a callback function but "
                                   "no callback defined"
                                   ' yet for option "{0}"').format(
                                       self.impl_getname()))
            self._validate_calculator(callback,
                                      callback_params)
        if callback is not None:
            callback_params = self._build_calculator_params(callback,
                                                            callback_params,
                                                            'callback')
            # first part is validator
            val = getattr(self, '_val_call', (None,))[0]
            if not callback_params:
                val_call = (callback,)
            else:
                val_call = (callback, callback_params)
            self._val_call = (val, val_call)

    def impl_is_optiondescription(self) -> bool:
        return False

    def impl_is_dynoptiondescription(self) -> bool:
        return False

    def impl_getname(self) -> str:
        return self._name

    def _set_readonly(self) -> None:
        if isinstance(self._informations, dict):
            _setattr = object.__setattr__
            dico = self._informations
            keys = tuple(dico.keys())
            if len(keys) == 1:
                dico = dico['doc']
            else:
                dico = tuple([keys, tuple(dico.values())])
            _setattr(self, '_informations', dico)
            extra = getattr(self, '_extra', None)
            if extra is not None:
                _setattr(self, '_extra', tuple([tuple(extra.keys()), tuple(extra.values())]))

    def impl_is_readonly(self) -> str:
        # _path is None when initialise SymLinkOption
        return hasattr(self, '_path') and self._path is not None

    def impl_getproperties(self) -> FrozenSet[str]:
        return getattr(self, '_properties', frozenset())

    def _setsubdyn(self,
                   subdyn) -> None:
        self._subdyn = weakref.ref(subdyn)

    def issubdyn(self) -> bool:
        return getattr(self, '_subdyn', None) is not None

    def getsubdyn(self):
        return self._subdyn()

    def impl_getrequires(self):
        return getattr(self, '_requires', STATIC_TUPLE)

    def impl_get_callback(self):
        call = getattr(self, '_val_call', (None, None))[1]
        if call is None:
            ret_call = (None, None)
        elif len(call) == 1:
            ret_call = (call[0], None)
        else:
            ret_call = call
        return ret_call

    # ____________________________________________________________
    # information
    def impl_get_information(self,
                             key: str,
                             default: Any=undefined) -> Any:
        """retrieves one information's item

        :param key: the item string (ex: "help")
        """
        dico = self._informations
        if isinstance(dico, tuple):
            if key in dico[0]:
                return dico[1][dico[0].index(key)]
        elif isinstance(dico, str):
            if key == 'doc':
                return dico
        elif isinstance(dico, dict):
            if key in dico:
                return dico[key]
        if default is not undefined:
            return default
        raise ValueError(_("information's item not found: {0}").format(
            key))

    def impl_set_information(self,
                             key: str,
                             value: Any) -> None:
        """updates the information's attribute
        (which is a dictionary)

        :param key: information's key (ex: "help", "doc"
        :param value: information's value (ex: "the help string")
        """
        if self.impl_is_readonly():
            raise AttributeError(_("'{0}' ({1}) object attribute '{2}' is"
                                   " read-only").format(self.__class__.__name__,
                                                        self,
                                                        #self.impl_getname(),
                                                        key))
        self._informations[key] = value


class BaseOption(Base):
    """This abstract base class stands for attribute access
    in options that have to be set only once, it is of course done in the
    __setattr__ method
    """
    __slots__ = tuple()

    def __getstate__(self):
        raise NotImplementedError()

    def __setattr__(self,
                    name: str,
                    value: Any) -> Any:
        """set once and only once some attributes in the option,
        like `_name`. `_name` cannot be changed once the option is
        pushed in the :class:`tiramisu.option.OptionDescription`.

        if the attribute `_readonly` is set to `True`, the option is
        "frozen" (which has nothing to do with the high level "freeze"
        propertie or "read_only" property)
        """
        # never change _name in an option or attribute when object is readonly
        if self.impl_is_readonly():
            raise AttributeError(_('"{}" ({}) object attribute "{}" is'
                                   ' read-only').format(self.__class__.__name__,
                                                        self.impl_get_display_name(),
                                                        name))
        super(BaseOption, self).__setattr__(name, value)

    def impl_getpath(self) -> str:
        try:
            return self._path
        except AttributeError:
            raise AttributeError(_('"{}" not part of any Config').format(self.impl_get_display_name()))

    def impl_has_callback(self) -> bool:
        "to know if a callback has been defined or not"
        return self.impl_get_callback()[0] is not None

    def impl_get_display_name(self,
                              dyn_name: Base=None) -> str:
        name = self.impl_get_information('doc')
        if name is None or name == '':
            if dyn_name is not None:
                name = dyn_name
            else:
                name = self.impl_getname()
        return name

    def reset_cache(self,
                    path: str,
                    values: Values,
                    settings: Settings,
                    resetted_opts: List[Base]) -> None:
        settings._p_.delcache(path)
        settings._pp_.delcache(path)
        if not self.impl_is_optiondescription():
            values._p_.delcache(path)

    def impl_is_symlinkoption(self) -> bool:
        return False


def validate_requires_arg(new_option: BaseOption,
                          multi: bool,
                          requires: List[dict],
                          name: str) -> Tuple[FrozenSet, Tuple]:
    """check malformed requirements
    and tranform dict to internal tuple

    :param requires: have a look at the
                     :meth:`tiramisu.setting.Settings.apply_requires` method to
                     know more about
                     the description of the requires dictionary
    """
    def get_option(require):
        if 'option' in require:
            option = require['option']
            if option == 'self':
                option = new_option
            if __debug__:
                if not isinstance(option, BaseOption):
                    raise ValueError(_('malformed requirements '
                                       'must be an option in option {0}').format(name))
                if not multi and option.impl_is_multi():
                    raise ValueError(_('malformed requirements '
                                       'multi option must not set '
                                       'as requires of non multi option {0}').format(name))
            option._add_dependency(new_option)
        else:
            callback = require['callback']
            callback_params = new_option._build_calculator_params(callback,
                                                                  require.get('callback_params'),
                                                                  'callback')
            option = (callback, callback_params)
        return option

    def _set_expected(action,
                      inverse,
                      transitive,
                      same_action,
                      option,
                      expected,
                      operator):
        if inverse not in ret_requires[action]:
            ret_requires[action][inverse] = ([(option, [expected])], action, inverse, transitive, same_action, operator)
        else:
            for exp in ret_requires[action][inverse][0]:
                if exp[0] == option:
                    exp[1].append(expected)
                    break
            else:
                ret_requires[action][inverse][0].append((option, [expected]))

    def set_expected(require,
                     ret_requires):
        expected = require['expected']
        inverse = get_inverse(require)
        transitive = get_transitive(require)
        same_action = get_sameaction(require)
        operator = get_operator(require)
        if isinstance(expected, list):
            for exp in expected:
                if __debug__ and set(exp.keys()) != {'option', 'value'}:
                    raise ValueError(_('malformed requirements expected must have '
                                       'option and value for option {0}').format(name))
                option = get_option(exp)
                if __debug__:
                    try:
                        option._validate(exp['value'], undefined)
                    except ValueError as err:
                        raise ValueError(_('malformed requirements expected value '
                                           'must be valid for option {0}'
                                           ': {1}').format(name, err))
                _set_expected(action,
                              inverse,
                              transitive,
                              same_action,
                              option,
                              exp['value'],
                              operator)
        else:
            option = get_option(require)
            if __debug__ and not isinstance(option, tuple) and expected is not None:
                try:
                    option._validate(expected, undefined)
                except ValueError as err:
                    raise ValueError(_('malformed requirements expected value '
                                       'must be valid for option {0}'
                                       ': {1}').format(name, err))
            _set_expected(action,
                          inverse,
                          transitive,
                          same_action,
                          option,
                          expected,
                          operator)

    def get_action(require):
        action = require['action']
        if action == 'force_store_value':
            raise ValueError(_("malformed requirements for option: {0}"
                               " action cannot be force_store_value"
                               ).format(name))
        return action

    def get_inverse(require):
        inverse = require.get('inverse', False)
        if inverse not in [True, False]:
            raise ValueError(_('malformed requirements for option: {0}'
                               ' inverse must be boolean'))
        return inverse

    def get_transitive(require):
        transitive = require.get('transitive', True)
        if transitive not in [True, False]:
            raise ValueError(_('malformed requirements for option: {0}'
                               ' transitive must be boolean'))
        return transitive

    def get_sameaction(require):
        same_action = require.get('same_action', True)
        if same_action not in [True, False]:
            raise ValueError(_('malformed requirements for option: {0}'
                               ' same_action must be boolean'))
        return same_action

    def get_operator(require):
        operator = require.get('operator', 'or')
        if operator not in ['and', 'or']:
            raise ValueError(_('malformed requirements for option: "{0}"'
                               ' operator must be "or" or "and"').format(operator))
        return operator


    ret_requires = {}
    config_action = set()

    # start parsing all requires given by user (has dict)
    # transforme it to a tuple
    for require in requires:
        if __debug__:
            if not isinstance(require, dict):
                raise ValueError(_("malformed requirements type for option:"
                                   " {0}, must be a dict").format(name))
            valid_keys = ('option', 'expected', 'action', 'inverse', 'transitive',
                          'same_action', 'operator', 'callback', 'callback_params')
            unknown_keys = frozenset(require.keys()) - frozenset(valid_keys)
            if unknown_keys != frozenset():
                raise ValueError(_('malformed requirements for option: {0}'
                                 ' unknown keys {1}, must only '
                                 '{2}').format(name,
                                               unknown_keys,
                                               valid_keys))
            # {'expected': ..., 'option': ..., 'action': ...}
            # {'expected': [{'option': ..., 'value': ...}, ...}], 'action': ...}
            # {'expected': ..., 'callback': ..., 'action': ...}
            if not 'expected' in require or not 'action' in require or \
                    not (isinstance(require['expected'], list) or \
                        'option' in require or \
                        'callback' in require):
                raise ValueError(_("malformed requirements for option: {0}"
                                   " require must have option, expected and"
                                   " action keys").format(name))
        action = get_action(require)
        config_action.add(action)
        if action not in ret_requires:
            ret_requires[action] = {}
        set_expected(require, ret_requires)

    # transform dict to tuple
    ret = []
    for requires in ret_requires.values():
        ret_action = []
        for require in requires.values():
            ret_action.append((tuple(require[0]), require[1],
                               require[2], require[3], require[4], require[5]))
        ret.append(tuple(ret_action))
    return frozenset(config_action), tuple(ret)
