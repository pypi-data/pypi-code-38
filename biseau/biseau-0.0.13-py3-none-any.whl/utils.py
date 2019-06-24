# encoding: utf8
"""Various helpers"""

import os
import inspect
from functools import partial, wraps
from collections import defaultdict


HANDLED_COLORS = {'red', 'green', 'blue'}


def color_from_colors(colors:set) -> str:
    """Return one color that represents the given ones"""
    if all(color in HANDLED_COLORS for color in colors):

        if len(colors) == 1: return next(iter(colors))
        if len(colors) == 2:
            if 'red' in colors:
                if 'blue' in colors: return 'magenta'
                else: return 'yellow'  # red and green
            else: return 'cyan'  # blue and green
        if len(colors) == 3: return 'white'
    elif len(colors) == 1:  # special case where only one non handled color is given
        return next(iter(colors))
    raise ValueError('UNVALID COLORS: ' + ', '.join(colors))


def normalized_path(path:str) -> str:
    return os.path.expanduser(os.path.abspath(os.path.expanduser(path)))


def join_on_genstr(funcgen:callable, joiner:str='') -> str:
    """If funcgen is a generator, will join its result on call

    >>> join_on_genstr(lambda: 'abc')()
    'abc'
    >>> def g(): yield from 'abc'
    >>> join_on_genstr(g)()
    'abc'
    >>> def g(c): return c+'bc'
    >>> join_on_genstr(g)('a')
    'abc'

    """
    if inspect.isgeneratorfunction(funcgen) or inspect.isgenerator(funcgen):
        return wraps(funcgen)(lambda *a, **k: joiner.join(funcgen(*a, **k)))
    return funcgen


def compile_python_code(code:str) -> dict:
    return compile(code, '<string>', 'exec')
def run_compiled_python_code(code:'code', namespace:dict=None) -> dict:
    namespace = namespace or {}
    exec(code, namespace)
    return namespace
def run_python_code(code:str, namespace:dict=None) -> dict:
    """

    >>> run_python_code('a = 1')['a']
    1
    >>> b = 1
    >>> run_python_code('b = 2')['b']
    2
    >>> b
    1

    """
    return run_compiled_python_code(compile_python_code(code), namespace or {})


def ispartialsubclass(obj:object, cls:object or (object,)) -> bool:
    return ispartial(obj, cls, subclass=True)
def ispartialinstance(obj:object, cls:object or (object,)) -> bool:
    return ispartial(obj, cls, instance=True)

def ispartial(obj:object, cls:object or (object,), subclass:bool=False,
              instance:bool=False) -> bool:
    if obj is cls: return True
    while type(obj) is partial:
        obj = obj.func

    # make it a tuple
    clss = cls if isinstance(cls, tuple) and obj is not tuple else (cls,)

    if subclass and instance:
        raise ValueError("Can't test for both subclass and instance")
    if subclass:
        test = lambda obj, cls: type(obj) is type and issubclass(obj, cls)
    elif instance:
        test = lambda obj, cls: isinstance(obj, cls)
    else:
        test = lambda obj, cls: obj is cls
    return any(test(obj, cls) for cls in clss)


def reverse_dict(d:dict, aggregator=set, multiple_values:bool=False) -> dict:
    """Return a new dict containing keys as values (aggregated into an `aggregator`)
    and values as keys.

    >>> sorted(tuple(reverse_dict({1: 2, 2: 3, 4: 2}).items()))
    [(2, {1, 4}), (3, {2})]

    """
    out = defaultdict(list)
    if multiple_values:
        for key, vals in d.items():
            for val in vals:
                out[val].append(key)
    else:
        for key, val in d.items():
            out[val].append(key)
    return {key: aggregator(val) for key, val in out.items()}


def name_to_identifier(name:str, replacement:str='_') -> str:
    """Return given name, modified with underscores in order to obtain a python identifier

    >>> name_to_identifier('a')
    'a'
    >>> name_to_identifier('a(b)')
    'a_b_'
    >>> name_to_identifier('3_2')
    '_3_2'
    >>> name_to_identifier('3_2')
    '_3_2'
    >>> name_to_identifier('\\\\')
    '_'

    """
    if not name:  return name
    if name[0].isdigit():  # what if it starts with a digit ?
        name = replacement + name
    name = ''.join(c if c.isidentifier() or c.isdigit() else replacement
                   for c in name)
    assert name.isidentifier(), f"there is a bug with function name_to_identifier with input '{name}'"
    return name
