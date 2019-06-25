from functools import partial
from infix import make_infix

from categories import instances
from categories.instances import Instances, Getter  # noqa: F401
from categories.instances import Adder, Undefiner  # noqa: F401
from categories.utils import compose, id_


__instances = {}  # type: Instances
get_instance = instances.make_getter(__instances, 'Functor')  # type: Getter
_add_instance = instances.make_adder(__instances)  # type: Adder
undefine_instance = instances.make_undefiner(__instances)  # type: Undefiner


class Functor:
    def __init__(self, fmap):
        self.fmap = fmap


def instance(type, fmap):
    instance = Functor(fmap)
    _add_instance(type, instance)
    return instance


@make_infix('or')
def fmap(f, x):
    instance = get_instance(type(x))
    return instance.fmap(f, x)


fp = fmap


def identity_law(x):
    """
    fmap id == id
    """
    return fmap(id_, x) == id_(x)


def composition_law(f, g, x):
    """
    fmap (g . f) == fmap g . fmap f
    """
    composed_funcs = compose(g, f)
    composed_fmaps = compose(partial(fmap, g), partial(fmap, f))
    return fmap(composed_funcs, x) == composed_fmaps(x)
