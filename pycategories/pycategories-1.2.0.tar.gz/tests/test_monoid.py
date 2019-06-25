import pytest

from categories import mappend, mempty, monoid, mp
from .sample_classes import Sequence


def _define_good_monoid():
    """Define a monoid instance that obeys the monoid laws."""
    monoid.undefine_instance(Sequence)
    monoid.instance(Sequence,
                    lambda: Sequence(),
                    lambda x, y: Sequence(*(x.items + y.items)))


def _define_bad_monoid():
    """
    Define a monoid instance that does not obey the monoid laws
    so we can test that the law functions correctly return False
    """
    monoid.undefine_instance(Sequence)
    monoid.instance(Sequence,
                    lambda: Sequence(42),
                    lambda x, y: Sequence(*(x.items + ("not", "good"))))


def test_monoid_instance_mappend():
    monoid.instance(int, lambda: 1, lambda a, b: a * b)
    assert mappend(2, 3, 5) == 30
    monoid.undefine_instance(int)


def test_infix_mappend():
    monoid.instance(int, lambda: 1, lambda a, b: a * b)
    assert 2 |mappend| 3 |mappend| 5 == 30
    assert 2 |mp| 3 |mp| 5 == 30
    monoid.undefine_instance(int)


def test_monoid_instance_mempty():
    monoid.instance(int, lambda: 0, lambda a, b: a + b)
    assert mempty(int) == 0


def test_undefined_instance():
    monoid.undefine_instance(int)
    with pytest.raises(TypeError):
        mappend(12, 3)
    with pytest.raises(TypeError):
        12 |mappend| 3
    with pytest.raises(TypeError):
        12 |mp| 3


def test_identity_law_true():
    _define_good_monoid()
    assert monoid.identity_law(Sequence(2, 3, 5, "test"))


def test_identity_law_false():
    _define_bad_monoid()
    assert not monoid.identity_law(Sequence(2, 3, 5, "test"))


def test_associativity_law_true():
    _define_good_monoid()
    x = Sequence(2, 3, 5)
    y = Sequence(7, 11, 13)
    z = Sequence(17, 19)
    assert monoid.associativity_law(x, y, z)


def test_associativity_law_false():
    _define_bad_monoid()
    x = Sequence(2, 3, 5)
    y = Sequence(7, 11, 13)
    z = Sequence(17, 19)
    assert not monoid.associativity_law(x, y, z)
