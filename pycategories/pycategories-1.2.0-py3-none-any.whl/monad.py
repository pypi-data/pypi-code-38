from functools import reduce
from infix import make_infix

from categories import instances
from categories.instances import Instances, Getter  # noqa: F401
from categories.instances import Adder, Undefiner  # noqa: F401


__instances = {}  # type: Instances
get_instance = instances.make_getter(__instances, 'Monad')  # type: Getter
_add_instance = instances.make_adder(__instances)  # type: Adder
undefine_instance = instances.make_undefiner(__instances)  # type: Undefiner


class Monad:
    def __init__(self, bind, mreturn):
        self.bind = bind
        self.mreturn = mreturn


def instance(type, mreturn, bind):
    instance = Monad(bind, mreturn)
    _add_instance(type, instance)
    return instance


@make_infix('or')
def bind(m, *fs):
    instance = get_instance(type(m))
    return reduce(instance.bind, (m,) + fs)


def mreturn(x, _type, type_form=None):
    kwargs = {'type_form': type_form} if type_form else {}
    instance = get_instance(_type)
    return instance.mreturn(x, **kwargs)


def left_identity_law(a, f, _type, type_form=None):
    """
    mreturn a >>= f == f a
    """
    mreturn_args = {'type_form': type_form} if type_form else {}
    return bind(mreturn(a, _type, **mreturn_args), f) == f(a)


def right_identity_law(m, type_form=None):
    """
    m >>= return == m

    Ex:
      Just 7 >>= return == Just 7
    """
    mreturn_args = {'type_form': type_form} if type_form else {}
    f = lambda x: mreturn(x, type(m), **mreturn_args)
    return bind(m, f) == m


def associativity_law(m, f, g, type_form=None):
    r"""
    (m >>= f) >>= g == m >>= (\x -> f x >>= g)
    """
    return bind(bind(m, f), g) == bind(m, lambda x: bind(f(x), g))
