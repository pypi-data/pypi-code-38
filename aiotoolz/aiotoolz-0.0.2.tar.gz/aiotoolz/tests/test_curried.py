import aiotoolz
import aiotoolz.curried
from aiotoolz.curried import (take, first, second, sorted, merge_with, reduce,
                           merge, operator as cop)
from collections import defaultdict
from importlib import import_module
from operator import add


def test_take():
    assert list(take(2)([1, 2, 3])) == [1, 2]


def test_first():
    assert first is aiotoolz.itertoolz.first


def test_merge():
    assert merge(factory=lambda: defaultdict(int))({1: 1}) == {1: 1}
    assert merge({1: 1}) == {1: 1}
    assert merge({1: 1}, factory=lambda: defaultdict(int)) == {1: 1}


def test_merge_with():
    assert merge_with(sum)({1: 1}, {1: 2}) == {1: 3}


def test_merge_with_list():
    assert merge_with(sum, [{'a': 1}, {'a': 2}]) == {'a': 3}


def test_sorted():
    assert sorted(key=second)([(1, 2), (2, 1)]) == [(2, 1), (1, 2)]


def test_reduce():
    assert reduce(add)((1, 2, 3)) == 6


def test_module_name():
    assert aiotoolz.curried.__name__ == 'aiotoolz.curried'


def test_curried_operator():
    for k, v in vars(cop).items():
        if not callable(v):
            continue

        if not isinstance(v, aiotoolz.curry):
            try:
                # Make sure it is unary
                v(1)
            except TypeError:
                try:
                    v('x')
                except TypeError:
                    pass
                else:
                    continue
                raise AssertionError(
                    'aiotoolz.curried.operator.%s is not curried!' % k,
                )

    # Make sure this isn't totally empty.
    assert len(set(vars(cop)) & {'add', 'sub', 'mul'}) == 3


def test_curried_namespace():
    exceptions = import_module('aiotoolz.curried.exceptions')
    namespace = {}

    def should_curry(func):
        if not callable(func) or isinstance(func, aiotoolz.curry):
            return False
        nargs = aiotoolz.functoolz.num_required_args(func)
        if nargs is None or nargs > 1:
            return True
        return nargs == 1 and aiotoolz.functoolz.has_keywords(func)


    def curry_namespace(ns):
        return {
            name: aiotoolz.curry(f) if should_curry(f) else f
            for name, f in ns.items() if '__' not in name
        }

    from_toolz = curry_namespace(vars(aiotoolz))
    from_exceptions = curry_namespace(vars(exceptions))
    namespace.update(aiotoolz.merge(from_toolz, from_exceptions))

    namespace = aiotoolz.valfilter(callable, namespace)
    curried_namespace = aiotoolz.valfilter(callable, aiotoolz.curried.__dict__)

    if namespace != curried_namespace:
        missing = set(namespace) - set(curried_namespace)
        if missing:
            raise AssertionError('There are missing functions in aiotoolz.curried:\n    %s'
                                 % '    \n'.join(sorted(missing)))
        extra = set(curried_namespace) - set(namespace)
        if extra:
            raise AssertionError('There are extra functions in aiotoolz.curried:\n    %s'
                                 % '    \n'.join(sorted(extra)))
        unequal = aiotoolz.merge_with(list, namespace, curried_namespace)
        unequal = aiotoolz.valfilter(lambda x: x[0] != x[1], unequal)
        messages = []
        for name, (orig_func, auto_func) in sorted(unequal.items()):
            if name in from_exceptions:
                messages.append('%s should come from aiotoolz.curried.exceptions' % name)
            elif should_curry(getattr(aiotoolz, name)):
                messages.append('%s should be curried from aiotoolz' % name)
            else:
                messages.append('%s should come from aiotoolz and NOT be curried' % name)
        raise AssertionError('\n'.join(messages))
