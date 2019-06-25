import pytest

from categories import applicative
from categories import ap, apply, pure
from .sample_classes import Wrapper


def _wrapper_pure(x):
    return Wrapper(x)


def _wrapper_apply(f, x):
    return pure(f.val(x.val), Wrapper)


def _define_good_applicative():
    """Define an applicative instance that obeys the applicative laws."""
    applicative.undefine_instance(Wrapper)
    applicative.instance(Wrapper, _wrapper_pure, _wrapper_apply)


def _define_bad_applicative():
    """
    Define an applicative instance that does not obey the applicative laws
    so we can test that the law functions correctly return False
    """
    applicative.undefine_instance(Wrapper)
    applicative.instance(Wrapper,
                         lambda x: Wrapper('nope'),
                         lambda f, x: str(x).upper())


def test_applicative_instance_pure():
    _define_good_applicative()
    assert pure('abc', Wrapper) == Wrapper('abc')
    applicative.undefine_instance(Wrapper)


def test_applicative_instance_apply():
    _define_good_applicative()
    f = Wrapper(lambda x: x.upper())
    x = Wrapper('abc')
    assert apply(f, x) == Wrapper('ABC')
    applicative.undefine_instance(Wrapper)


def test_infix_apply():
    _define_good_applicative()
    f = Wrapper(lambda x: x.upper())
    x = Wrapper('abc')
    assert f |apply| x == Wrapper('ABC')
    assert f |ap| x == Wrapper('ABC')
    applicative.undefine_instance(Wrapper)


def test_undefined_instance():
    applicative.undefine_instance(Wrapper)
    with pytest.raises(TypeError, match="No instance for"):
        pure('abc', Wrapper)


def test_identity_law_true():
    _define_good_applicative()
    assert applicative.identity_law(Wrapper(17))


def test_identity_law_false():
    _define_bad_applicative()
    assert not applicative.identity_law(Wrapper(17))


def test_homomorphism_law_true():
    _define_good_applicative()
    f = lambda x: x ** 2
    x = 18
    assert applicative.homomorphism_law(f, x, Wrapper)


def test_homomorphism_law_false():
    _define_bad_applicative()
    f = lambda x: x ** 2
    x = 18
    assert not applicative.homomorphism_law(f, x, Wrapper)


def test_interchange_law_true():
    _define_good_applicative()
    u = Wrapper(lambda x: x ** 2)
    y = 7
    assert applicative.interchange_law(u, y)


def test_interchange_law_false():
    _define_bad_applicative()
    u = Wrapper(lambda x: x ** 2)
    y = 7
    assert not applicative.interchange_law(u, y)
