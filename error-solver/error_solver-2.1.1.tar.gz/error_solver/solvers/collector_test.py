import pytest
from math import pi
from .collector import *


# Collector test class
class Circle(object):
    def __init__(self, r):
        self.r = r

    @collect
    def area(self):
        return pi*self.r**2


# Collector test function
@fcollect
def area(r):
    return pi*r**2


def test_collector():
    with Collector() as collector:
        c1 = Circle(1)
        c2 = Circle(2)

        a1 = c1.area()
        a2 = c2.area()

        assert collector.get(c1) == {'area': a1}
        assert collector.get(c2) == {'area': a2}

        b1 = area(1)
        b2 = area(2)

        assert collector.fget(area) != b1
        assert collector.fget(area) == b2

        assert collector.get_dict() == {c1: {'area': a1}, c2: {'area': a2}}
        assert collector.get_fdict() == {'{}.{}'.format(area.__module__, area.__name__): b2}

    assert len(collector.get_dict()) == 0
    assert len(collector.get_fdict()) == 0


def test_nested_collector():
    with Collector():
        with pytest.raises(ValueError):
            with Collector():
                pass


def test_bad_keys():
    with Collector() as collector:
        assert collector.get('bad_key', None) is None

        with pytest.raises(KeyError):
            collector.get('bad_key')

        assert collector.fget(area, None) is None

        with pytest.raises(KeyError):
            collector.fget(area)
