import random

import pytest

from categories import fmap, fp, functor
from .sample_classes import Pair


random.seed(0)


def _define_good_functor():
    """Define a functor instance that obeys the functor laws."""
    functor.undefine_instance(Pair)
    functor.instance(Pair, lambda f, x: Pair(x.a, f(x.b)))


def _define_bad_functor():
    """
    Define a functor instance that does not obey the functor laws
    so we can test that the law functions correctly return False
    """
    functor.undefine_instance(Pair)
    functor.instance(Pair, lambda f, x: Pair("bad", random.randint(0, 10e9)))


def test_functor_instance_fmap():
    _define_good_functor()
    pair = Pair('a', 12)
    test = fmap(lambda x: x * 3, pair)
    assert test == Pair('a', 36)


def test_infix_fmap():
    _define_good_functor()
    pair = Pair('a', 12)
    assert (lambda x: x * 3) |fmap| pair == Pair('a', 36)
    assert (lambda x: x * 3) |fp| pair == Pair('a', 36)


def test_undefined_instance():
    functor.undefine_instance(Pair)
    with pytest.raises(TypeError):
        fmap(lambda x: x + 1, Pair('a', 2))
    with pytest.raises(TypeError):
        (lambda x: x + 1) |fmap| Pair('a', 2)
    with pytest.raises(TypeError):
        (lambda x: x + 1) |fp| Pair('a', 2)


def test_identity_law_true():
    _define_good_functor()
    assert functor.identity_law(Pair("test", 42))


def test_identity_law_false():
    _define_bad_functor()
    assert not functor.identity_law(Pair("test", 42))


def test_composition_law_true():
    _define_good_functor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert functor.composition_law(f, g, x)


def test_composition_law_false():
    _define_bad_functor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert not functor.composition_law(f, g, x)
