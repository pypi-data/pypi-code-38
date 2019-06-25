import random

from categories import monad
from categories import bind, mreturn
from .sample_classes import Wrapper

random.seed(0)


def _define_good_monad():
    """Define a monad instance that obeys the monad laws."""
    monad.undefine_instance(Wrapper)
    monad.instance(Wrapper,
                   lambda x: Wrapper(x),
                   lambda m, f: f(m.val))


def _define_bad_monad():
    """
    Define a monad instance that does not obey the monad laws
    so we can test that the law functions correctly return False
    """
    monad.undefine_instance(Wrapper)
    monad.instance(Wrapper,
                   lambda x: Wrapper("really really bad {}".format(
                       random.randint(0, 10e9))),
                   lambda m, f: Wrapper("I'm bad {}".format(
                       random.randint(0, 10e9))))


def test_bind():
    _define_good_monad()
    assert bind(Wrapper(12), lambda x: Wrapper(x ** 2)) == Wrapper(144)


def test_bind_infix():
    _define_good_monad()
    assert Wrapper(12) |bind| (lambda x: Wrapper(x ** 2)) == Wrapper(144)


def test_bind_multiple_functions():
    _define_good_monad()
    x = Wrapper(16)
    f = lambda x: Wrapper(x / 4)
    g = lambda x: Wrapper(x * 3)
    h = lambda x: Wrapper(x + 17)
    assert bind(x, f, g, h) == Wrapper(16 / 4 * 3 + 17)


def test_mreturn():
    _define_good_monad()
    assert mreturn(17, Wrapper) == Wrapper(17)


def test_left_identity_law_true():
    _define_good_monad()
    a = "test"
    f = lambda x: Wrapper(x.capitalize())
    assert monad.left_identity_law(a, f, Wrapper)


def test_left_identity_law_false():
    _define_bad_monad()
    a = "test"
    f = lambda x: Wrapper(x.capitalize())
    assert not monad.left_identity_law(a, f, Wrapper)


def test_right_identity_law_true():
    _define_good_monad()
    assert monad.right_identity_law(Wrapper("test"))


def test_right_identity_law_false():
    _define_bad_monad()
    assert not monad.right_identity_law(Wrapper("test"))


def test_associativity_law_true():
    _define_good_monad()
    m = Wrapper(10)
    f = lambda x: Wrapper(x * 2)
    g = lambda x: Wrapper(x + 3)
    assert monad.associativity_law(m, f, g)


def test_associativity_law_false():
    _define_bad_monad()
    m = Wrapper("test")
    f = lambda x: Wrapper(x * "ing")
    g = lambda x: Wrapper(x + " stuff")
    assert not monad.associativity_law(m, f, g)
