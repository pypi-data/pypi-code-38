import random

import pytest

from categories import first, second, bimap, bifunctor
from .sample_classes import Pair


random.seed(0)


def _define_good_bifunctor():
    """Define a bifunctor instance that obeys the functor laws."""
    bifunctor.undefine_instance(Pair)
    bifunctor.instance(
        Pair,
        lambda f, x: Pair(f(x.a), x.b),
        lambda f, x: Pair(x.a, f(x.b)))


def _define_bad_bifunctor():
    """
    Define a bifunctor instance that does not obey the functor laws
    so we can test that the law functions correctly return False
    """
    bifunctor.undefine_instance(Pair)
    bifunctor.instance(
        Pair,
        lambda f, x: Pair("bad", random.randint(0, 10e9)),
        lambda f, x: Pair("bad", random.randint(0, 10e9)))


def test_bifunctor_instance_first():
    _define_good_bifunctor()
    pair = Pair('a', 12)
    test = first(lambda x: x * 3, pair)
    assert test == Pair('aaa', 12)


def test_bifunctor_instance_second():
    _define_good_bifunctor()
    pair = Pair('a', 12)
    test = second(lambda x: x * 3, pair)
    assert test == Pair('a', 36)


def test_bifunctor_instance_bimap():
    _define_good_bifunctor()
    pair = Pair('a', 12)
    f = lambda x: x * 3
    test = bimap(f, f, pair)
    assert test == Pair('aaa', 36)


def test_undefined_instance():
    bifunctor.undefine_instance(Pair)
    with pytest.raises(TypeError):
        first(lambda x: x + 1, Pair(2, 'a'))
    with pytest.raises(TypeError):
        second(lambda x: x + 1, Pair(2, 'a'))
    with pytest.raises(TypeError):
        f = lambda x: x + 1
        bimap(f, f, Pair(2, 'a'))


def test_identity_law_true():
    _define_good_bifunctor()
    assert bifunctor.first_identity_law(Pair("test", 42))
    assert bifunctor.second_identity_law(Pair("test", 42))
    assert bifunctor.bimap_identity_law(Pair("test", 42))


def test_identity_law_false():
    _define_bad_bifunctor()
    assert not bifunctor.first_identity_law(Pair("test", 42))
    assert not bifunctor.second_identity_law(Pair("test", 42))
    assert not bifunctor.bimap_identity_law(Pair("test", 42))


def test_first_composition_law_true():
    _define_good_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert bifunctor.first_composition_law(f, g, x)


def test_first_composition_law_false():
    _define_bad_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert not bifunctor.first_composition_law(f, g, x)


def test_second_composition_law_true():
    _define_good_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert bifunctor.second_composition_law(f, g, x)


def test_second_composition_law_false():
    _define_bad_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert not bifunctor.second_composition_law(f, g, x)


def test_bifunctor_composition_law_true():
    _define_good_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert bifunctor.bifunctor_composition_law(f, g, x)


def test_bifunctor_composition_law_false():
    _define_bad_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    x = Pair("good", "TEST")
    assert not bifunctor.bifunctor_composition_law(f, g, x)


def test_bimap_composition_law_true():
    _define_good_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    h = lambda x: x.title()
    i = lambda x: x.swapcase()
    x = Pair("good", "TEST")
    assert bifunctor.bimap_composition_law(f, g, h, i, x)


def test_bimap_composition_law_false():
    _define_bad_bifunctor()
    f = lambda x: x.lower()
    g = lambda x: x.capitalize()
    h = lambda x: x.title()
    i = lambda x: x.swapcase()
    x = Pair("good", "TEST")
    assert not bifunctor.bimap_composition_law(f, g, h, i, x)
