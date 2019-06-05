# Copyright (C) 2018-2019 Team tiramisu (see AUTHORS for all contributors)
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
from typing import Any, List, Optional
from operator import add, mul, sub, truediv
from .setting import undefined
from .i18n import _


class Params:
    __slots__ = ('args', 'kwargs')
    def __init__(self, args=None, kwargs=None, **kwgs):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        if kwgs:
            kwargs.update(kwgs)
        if isinstance(args, Param):
            args = (args,)
        else:
            if not isinstance(args, tuple):
                raise ValueError(_('args in params must be a tuple'))
            for arg in args:
                if not isinstance(arg, Param):
                    raise ValueError(_('arg in params must be a Param'))
        if not isinstance(kwargs, dict):
            raise ValueError(_('kwargs in params must be a dict'))
        for arg in kwargs.values():
            if not isinstance(arg, Param):
                raise ValueError(_('arg in params must be a Param'))
        self.args = args
        self.kwargs = kwargs


class Param:
    pass


class ParamOption(Param):
    __slots__ = ('option',
                 'notraisepropertyerror')
    def __init__(self,
                 option: 'Option',
                 notraisepropertyerror: bool=False) -> None:
        if __debug__ and not hasattr(option, 'impl_is_symlinkoption'):
            raise ValueError(_('paramoption needs an option not {}').format(type(option)))
        if option.impl_is_symlinkoption():
            cur_opt = option.impl_getopt()
        else:
            cur_opt = option
        if not isinstance(notraisepropertyerror, bool):
            raise ValueError(_('param must have a boolean'
                               ' not a {} for notraisepropertyerror'
                              ).format(type(notraisepropertyerror)))

        self.option = cur_opt
        self.notraisepropertyerror = notraisepropertyerror


class ParamValue(Param):
    __slots__ = ('value',)
    def __init__(self, value):
        self.value = value


class ParamContext(Param):
    __slots__ = tuple()


class ParamIndex(Param):
    __slots__ = tuple()


def tiramisu_copy(val):  # pragma: no cover
    return val


def calc_value(*args: List[Any],
               multi: bool=False,
               default: Any=undefined,
               condition: Any=undefined,
               expected: Any=undefined,
               condition_operator: str='AND',
               allow_none: bool=False,
               remove_duplicate_value: bool=False,
               join: Optional[str]=None,
               min_args_len: Optional[int]=None,
               operator: Optional[str]=None,
               index: Optional[int]=None,
               **kwargs) -> Any:
    """calculate value
    :param multi: value returns must be a list of value
    :param default: default value if condition is not matched or if args is empty
                    if there is more than one default value, set default_0, default_1, ...
    :param condition: test if condition is equal to expected value
                      if there is more than one condition, set condition_0, condition_1, ...
    :param expected: value expected for all conditions
                     if expected value is different between condition, set expected_0, expected_1, ...
    :param condition_operator: OR or AND operator for condition
    :param allow_none: if False, do not return list in None is present in list
    :param remove_duplicate_value: if True, remote duplicated value
    :param join: join all args with specified characters
    :param min_args_len: if number of arguments is smaller than this value, return default value
    :param operator: operator

    examples:
    * you want to copy value from an option to an other option:
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption
    >>> val1 = StrOption('val1', '', 'val1')
    >>> val2 = StrOption('val2', '', callback=calc_value, callback_params=Params(ParamOption(val1)))
    >>> od = OptionDescription('root', '', [val1, val2])
    >>> cfg = Config(od)
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val1'}

    * you want to copy values from two options in one multi option
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = StrOption('val1', "", 'val1')
    >>> val2 = StrOption('val2', "", 'val2')
    >>> val3 = StrOption('val3', "", multi=True, callback=calc_value, callback_params=Params((ParamOption(val1), ParamOption(val2)), multi=ParamValue(True)))
    >>> od = OptionDescription('root', '', [val1, val2, val3])
    >>> cfg = Config(od)
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val2', 'val3': ['val1', 'val2']}

    * you want to copy a value from an option is it not disabled, otherwise set 'default_value'
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = StrOption('val1', '', 'val1')
    >>> val2 = StrOption('val2', '', callback=calc_value, callback_params=Params(ParamOption(val1, True), default=ParamValue('default_value')))
    >>> od = OptionDescription('root', '', [val1, val2])
    >>> cfg = Config(od)
    >>> cfg.property.read_write()
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val1'}
    >>> cfg.option('val1').property.add('disabled')
    >>> cfg.value.dict()
    {'val2': 'default_value'}

    * you want to copy value from an option is an other is True, otherwise set 'default_value'
    >>> from tiramisu import calc_value, BoolOption, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> boolean = BoolOption('boolean', '', True)
    >>> val1 = StrOption('val1', '', 'val1')
    >>> val2 = StrOption('val2', '', callback=calc_value, callback_params=Params(ParamOption(val1, True),
    ...                                                                          default=ParamValue('default_value'),
    ...                                                                          condition=ParamOption(boolean),
    ...                                                                          expected=ParamValue(True)))
    >>> od = OptionDescription('root', '', [boolean, val1, val2])
    >>> cfg = Config(od)
    >>> cfg.property.read_write()
    >>> cfg.value.dict()
    {'boolean': True, 'val1': 'val1', 'val2': 'val1'}
    >>> cfg.option('boolean').value.set(False)
    >>> cfg.value.dict()
    {'boolean': False, 'val1': 'val1', 'val2': 'default_value'}

    * you want to copy option even if None is present
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = StrOption('val1', "", 'val1')
    >>> val2 = StrOption('val2', "")
    >>> val3 = StrOption('val3', "", multi=True, callback=calc_value, callback_params=Params((ParamOption(val1), ParamOption(val2)), multi=ParamValue(True), allow_none=ParamValue(True)))
    >>> od = OptionDescription('root', '', [val1, val2, val3])
    >>> cfg = Config(od)
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': None, 'val3': ['val1', None]}

    * you want uniq value
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = StrOption('val1', "", 'val1')
    >>> val2 = StrOption('val2', "", 'val1')
    >>> val3 = StrOption('val3', "", multi=True, callback=calc_value, callback_params=Params((ParamOption(val1), ParamOption(val2)), multi=ParamValue(True), remove_duplicate_value=ParamValue(True)))
    >>> od = OptionDescription('root', '', [val1, val2, val3])
    >>> cfg = Config(od)
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val1', 'val3': ['val1']}

    * you want to join two values with '.'
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = StrOption('val1', "", 'val1')
    >>> val2 = StrOption('val2', "", 'val2')
    >>> val3 = StrOption('val3', "", callback=calc_value, callback_params=Params((ParamOption(val1), ParamOption(val2)), join=ParamValue('.')))
    >>> od = OptionDescription('root', '', [val1, val2, val3])
    >>> cfg = Config(od)
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val2', 'val3': 'val1.val2'}

    * you want join three values, only if almost three values are set
    >>> from tiramisu import calc_value, StrOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = StrOption('val1', "", 'val1')
    >>> val2 = StrOption('val2', "", 'val2')
    >>> val3 = StrOption('val3', "", 'val3')
    >>> val4 = StrOption('val4', "", callback=calc_value, callback_params=Params((ParamOption(val1), ParamOption(val2), ParamOption(val3, True)), join=ParamValue('.'), min_args_len=ParamValue(3)))
    >>> od = OptionDescription('root', '', [val1, val2, val3, val4])
    >>> cfg = Config(od)
    >>> cfg.property.read_write()
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val2', 'val3': 'val3', 'val4': 'val1.val2.val3'}
    >>> cfg.option('val3').property.add('disabled')
    >>> cfg.value.dict()
    {'val1': 'val1', 'val2': 'val2', 'val4': ''}

    * you want to add all values
    >>> from tiramisu import calc_value, IntOption, OptionDescription, Config, Params, ParamOption, ParamValue
    >>> val1 = IntOption('val1', "", 1)
    >>> val2 = IntOption('val2', "", 2)
    >>> val3 = IntOption('val3', "", callback=calc_value, callback_params=Params((ParamOption(val1), ParamOption(val2)), operator=ParamValue('add')))
    >>> od = OptionDescription('root', '', [val1, val2, val3])
    >>> cfg = Config(od)
    >>> cfg.value.dict()
    {'val1': 1, 'val2': 2, 'val3': 3}

    """
    def value_from_kwargs(value: Any, pattern: str, to_dict: bool=False) -> Any:
        # if value attribute exist return it's value
        # otherwise pattern_0, pattern_1, ...
        # otherwise undefined
        if value is not undefined:
            if to_dict == 'all':
                returns = {0: value}
            else:
                returns = value
        else:
            kwargs_matches = {}
            len_pattern = len(pattern)
            for key in kwargs.keys():
                if key.startswith(pattern):
                    index = int(key[len_pattern:])
                    kwargs_matches[index] = kwargs[key]
            if not kwargs_matches:
                return undefined
            keys = sorted(kwargs_matches)
            if to_dict:
                returns = {}
            else:
                returns = []
            for key in keys:
                if to_dict:
                    returns[key] = kwargs_matches[key]
                else:
                    returns.append(kwargs_matches[key])
        return returns

    def is_condition_matches():
        calculated_conditions = value_from_kwargs(condition, 'condition_', to_dict='all')
        if condition is not undefined:
            is_matches = None
            calculated_expected = value_from_kwargs(expected, 'expected_', to_dict=True)
            for idx, calculated_condition in calculated_conditions.items():
                if isinstance(calculated_expected, dict):
                    current_matches = calculated_condition == calculated_expected[idx]
                else:
                    current_matches = calculated_condition == calculated_expected
                if is_matches is None:
                    is_matches = current_matches
                elif condition_operator == 'AND':
                    is_matches = is_matches and current_matches
                elif condition_operator == 'OR':
                    is_matches = is_matches or current_matches
                else:
                    raise ValueError(_('unexpected {} condition_operator in calc_value').format(condition_operator))
        else:
            is_matches = True
        return is_matches

    def get_value():
        if not is_condition_matches():
            # force to default
            value = []
        else:
            value = list(args)
        if min_args_len and not len(value) >= min_args_len:
            value = []
        if value == []:
            # default value
            new_default = value_from_kwargs(default, 'default_')
            if new_default is not undefined:
                if not isinstance(new_default, list):
                    value = [new_default]
                else:
                    value = new_default
        return value

    value = get_value()
    if not multi:
        if join is not None:
            value = join.join(value)
        elif value and operator:
            new_value = value[0]
            op = {'mul': mul,
                  'add': add,
                  'div': truediv,
                  'sub': sub}[operator]
            for val in value[1:]:
                new_value = op(new_value, val)
            value = new_value
        elif value == []:
            value = None
        else:
            value = value[0]
            if isinstance(value, list) and index is not None:
                if len(value) > index:
                    value = value[index]
                else:
                    value = None
    elif None in value and not allow_none:
        value = []
    elif remove_duplicate_value:
        new_value = []
        for val in value:
            if val not in new_value:
                new_value.append(val)
        value = new_value
    return value
