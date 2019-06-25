from functools import partial

from categories import instances
from categories.instances import Instances, Getter  # noqa: F401
from categories.instances import Adder, Undefiner  # noqa: F401
from categories.utils import compose, id_


__instances = {}  # type: Instances
get_instance = instances.make_getter(__instances, 'Bifunctor')  # type: Getter
_add_instance = instances.make_adder(__instances)  # type: Adder
undefine_instance = instances.make_undefiner(__instances)  # type: Undefiner


class Bifunctor:
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.bimap = lambda f, g, x: first(f, second(g, x))


def instance(type, first, second):
    instance = Bifunctor(first, second)
    _add_instance(type, instance)
    return instance


def first(f, x):
    instance = get_instance(type(x))
    return instance.first(f, x)


def second(f, x):
    instance = get_instance(type(x))
    return instance.second(f, x)


def bimap(f, g, x):
    instance = get_instance(type(x))
    return instance.bimap(f, g, x)


def first_identity_law(x):
    """
    first id == id
    """
    return first(id_, x) == id_(x)


def second_identity_law(x):
    """
    second id == id
    """
    return second(id_, x) == id_(x)


def bimap_identity_law(x):
    """
    bimap id id == id
    """
    return bimap(id_, id_, x) == id_(x)


def first_composition_law(f, g, x):
    """
    first (g . f) == first g . first f
    """
    composed_funcs = compose(g, f)
    composed_firsts = compose(partial(first, g), partial(first, f))
    return first(composed_funcs, x) == composed_firsts(x)


def second_composition_law(f, g, x):
    """
    second (g . f) == second g . second f
    """
    composed_funcs = compose(g, f)
    composed_seconds = compose(partial(second, g), partial(second, f))
    return second(composed_funcs, x) == composed_seconds(x)


def bifunctor_composition_law(f, g, x):
    """
    bimap f g == first f . second g
    """
    composed_fs = compose(partial(first, f), partial(second, g))
    return bimap(f, g, x) == composed_fs(x)


def bimap_composition_law(f, g, h, i, x):
    """
    bimap (f . g) (h . i) == bimap (f . h) . bimap (g . i)
    """
    fg = compose(f, g)
    hi = compose(h, i)
    composed_bimap = compose(partial(bimap, f, h), partial(bimap, g, i))
    return bimap(fg, hi, x) == composed_bimap(x)
