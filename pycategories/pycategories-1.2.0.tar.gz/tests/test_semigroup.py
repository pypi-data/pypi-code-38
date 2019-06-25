import pytest

from categories import sappend, semigroup, sp
from .sample_classes import Sequence


def _define_good_semigroup():
    """Define a semigroup instance that obeys the semigroup laws."""
    semigroup.undefine_instance(Sequence)
    semigroup.instance(Sequence,
                       lambda x, y: Sequence(*(x.items + y.items)))


def _define_bad_semigroup():
    """
    Define a semigroup instance that does not obey the semigroup laws
    so we can test that the law functions correctly return False
    """
    semigroup.undefine_instance(Sequence)
    semigroup.instance(Sequence,
                       lambda x, y: Sequence(*(x.items + ("not", "good"))))


def test_semigroup_instance_sappend():
    semigroup.instance(str, lambda a, b: a + b)
    assert sappend("this", " is ", "good") == "this is good"
    semigroup.undefine_instance(str)
    semigroup.instance(int, lambda a, b: str(a) + str(b))
    assert sappend(1, 0) == "10"
    semigroup.undefine_instance(int)


def test_sappend_infix():
    semigroup.instance(str, lambda a, b: a + b)
    assert "this" |sappend| " is " |sappend| "good" == "this is good"
    assert "this" |sp| " is " |sp| "good" == "this is good"
    semigroup.undefine_instance(str)


def test_undefined_instance():
    semigroup.undefine_instance(str)
    semigroup.undefine_instance(int)
    with pytest.raises(TypeError):
        sappend(1, 0)
    with pytest.raises(TypeError):
        sappend("no", "good")


def test_associativity_law_true():
    _define_good_semigroup()
    x = Sequence(2, 3, 5)
    y = Sequence(7, 11, 13)
    z = Sequence(17, 19)
    assert semigroup.associativity_law(x, y, z)


def test_associativity_law_false():
    _define_bad_semigroup()
    x = Sequence(2, 3, 5)
    y = Sequence(7, 11, 13)
    z = Sequence(17, 19)
    assert not semigroup.associativity_law(x, y, z)
