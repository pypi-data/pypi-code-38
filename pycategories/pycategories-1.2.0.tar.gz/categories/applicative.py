from infix import make_infix

from categories import instances
from categories.utils import compose, id_
from categories.instances import Instances, Getter  # noqa: F401
from categories.instances import Adder, Undefiner  # noqa: F401


__instances = {}  # type: Instances
get_instance = instances.make_getter(__instances,
                                     'Applicative')  # type: Getter
_add_instance = instances.make_adder(__instances)  # type: Adder
undefine_instance = instances.make_undefiner(__instances)  # type: Undefiner


class Applicative:
    def __init__(self, pure, apply):
        self.pure = pure
        self.apply = apply


def instance(type, pure, apply):
    instance = Applicative(pure, apply)
    _add_instance(type, instance)
    return instance


def pure(x, _type, type_form=None):
    """
    The optional type_form arg is an attempt to provide some more flexibility
    with the type that pure is required to cast to.  For example, pure for
    the tuple Applicative instance needs to know the types of its elements so
    it can return the correct object:

    pure(7, tuple, type_form=(str, int)) == ("", 7)
    """
    kwargs = {'type_form': type_form} if type_form else {}
    instance = get_instance(_type)
    return instance.pure(x, **kwargs)


@make_infix('or')
def apply(f, x):
    """
    Same as Haskell's <*> operator

    :param f: A function contained in an Applicative
    :param x: A value contained in the Applicative
    :return: f(x) contained in the Applicative
    """
    instance = get_instance(type(f))
    return instance.apply(f, x)


ap = apply


def identity_law(v, type_form=None):
    """
    pure id <*> v == v
      where (<*>) = apply
    """
    pure_args = {'type_form': type_form} if type_form else {}
    pure_id = pure(id_, type(v), **pure_args)
    return apply(pure_id, v) == v


def homomorphism_law(f, x, _type, type_form=None):
    """
    pure f <*> pure x == pure (f x)
      where (<*>) = apply
    """
    pure_args = {'type_form': type_form} if type_form else {}
    pure_f = pure(f, _type, **pure_args)
    pure_x = pure(x, _type, **pure_args)
    return apply(pure_f, pure_x) == pure(f(x), _type, **pure_args)


def interchange_law(u, y, type_form=None):
    """
    u <*> pure y == pure ($ y) <*> u
      where (<*>) = apply
    """
    pure_args = {'type_form': type_form} if type_form else {}
    pure_y = pure(y, type(u), **pure_args)
    pure_dollar_y = pure(lambda f: f(y), type(u), **pure_args)
    return apply(u, pure_y) == apply(pure_dollar_y, u)


def composition_law(u, v, w, type_form=None):  # pragma: no cover
    """
    pure (.) <*> u <*> v <*> w == u <*> (v <*> w)
      where (<*>) = apply
    """
    raise NotImplementedError("Applicative composition law not implemented")
    # TODO: having some problems here because of not being able to partially
    #       apply functions wrapped in Applicative.  This may not actually
    #       be possible without some sort of hack or workaround
    pure_compose = pure(compose, type(u))
    return apply(apply(apply(pure_compose, u), v), w) == \
        apply(u, apply(v, w))
