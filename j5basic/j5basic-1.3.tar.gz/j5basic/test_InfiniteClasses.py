#!/usr/bin/env python
from j5basic.InfiniteClasses import *
import sys

if sys.version_info.major > 2:
    # Python 3 doesn't have this
    def cmp(a, b):
        return (a > b) - (a < b)

class A(object):
    def __init__(self, v):
        self.value = v
    def __cmp__(self, other):
        if isinstance(other, A):
            return cmp(self.value, other.value)
        return cmp(self.value, other)

    def __lt__(self, other):
        return self.__cmp__(other) == -1

    def __le__(self, other):
        return self.__cmp__(other) < 1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __ge__(self, other):
        return self.__cmp__(other) > -1

    def __gt__(self, other):
        return self.__cmp__(other) == 1

class B():
    def __init__(self, v):
        self.value = v
    def __cmp__(self, other):
        if isinstance(other, B):
            return cmp(self.value, other.value)
        return cmp(self.value, other)

class C():
    def __init__(self, v):
        self.value = v
    def __cmp__(self, other):
        if isinstance(other, B):
            return cmp(self.value, other.value)
        return cmp(self.value, other)
    def __lt__(self, other):
        return self.__cmp__(other) == -1

class TestInfinite:

    def _do_comparisons(self, infinite_class, value):
        p_inf = infinite_class()
        n_inf = infinite_class(False)
        #positive infinity to negative infinity
        self._comp(p_inf, n_inf)
        #positive infinity to value
        self._comp(p_inf, value)
        #negative infinity to value
        self._comp(value, n_inf)

    def _comp(self, greater, lesser):
        assert cmp(greater, greater) == 0
        assert cmp(lesser, lesser) == 0
        assert cmp(greater, lesser) == 1
        assert cmp(lesser, greater) == -1
        assert greater > lesser
        assert greater >= lesser
        assert greater != lesser
        assert not (greater < lesser)
        assert not (greater <= lesser)
        assert not (greater == lesser)

        assert lesser < greater
        assert lesser <= greater
        assert lesser != greater
        assert not (lesser > greater)
        assert not (lesser >= greater)
        assert not (lesser == greater)

    def _do_compare_infinities(self, infinite_class):
        infinity1 = infinite_class()
        infinity2 = infinite_class()
        assert cmp(infinity1, infinity2) == 0
        assert infinity1 == infinity2
        assert infinity1 >= infinity2
        assert infinity1 <= infinity2
        assert not (infinity1 != infinity2)
        assert not (infinity1 > infinity2)
        assert not (infinity1 < infinity2)
        #negative infinity to negative infinity
        infinity1 = infinite_class(False)
        infinity2 = infinite_class(False)
        assert infinity1 == infinity2
        assert infinity1 >= infinity2
        assert infinity1 <= infinity2
        assert not (infinity1 != infinity2)
        assert not (infinity1 > infinity2)
        assert not (infinity1 < infinity2)

    def test_object_numeric(self):
        self._do_compare_infinities(InfiniteObject)
        self._do_comparisons(InfiniteObject, 99999999999999)
        self._do_comparisons(InfiniteObject, 1e200)
        infinity1 = InfiniteObject()
        infinity2 = float("inf")
        assert cmp(infinity1, infinity2) == 0
        assert infinity1 == infinity2
        assert infinity1 >= infinity2
        assert infinity1 <= infinity2
        assert not (infinity1 != infinity2)
        assert not (infinity1 > infinity2)
        assert not (infinity1 < infinity2)
        #negative infinity to negative infinity
        infinity1 = InfiniteObject(False)
        infinity2 = float("-inf")
        assert infinity1 == infinity2
        assert infinity1 >= infinity2
        assert infinity1 <= infinity2
        assert not (infinity1 != infinity2)
        assert not (infinity1 > infinity2)
        assert not (infinity1 < infinity2)

    def test_date(self):
        self._do_compare_infinities(InfiniteDate)
        self._do_comparisons(InfiniteDate, datetime.datetime.now())
        year = InfiniteDate().year
        assert isinstance(year,InfiniteObject)
        self._comp(year, datetime.MAXYEAR)

    def test_object(self):
        if sys.version_info.major > 2:
            # Python 3 doesn't support this use due to different rules for __new__
            return
        #Infinite Class implements rich comparisons. Should override parent class comparisons regardless of which side of the
        #comparison operator it is placed.
        class InfiniteA(InfiniteObject, A):
            def __new__(cls, positive=True):
                return super(InfiniteA,cls).__new__(cls, 1)
        self._do_compare_infinities(InfiniteA)
        self._do_comparisons(InfiniteA, A(35))

    def test_nonobject(self):
        if sys.version_info.major > 2:
            # Python 3 doesn't support this use due to different rules for __new__
            return
        #Case: Class does not implement rich comparisons
        class InfiniteB(InfiniteObject, B):
            def __new__(cls, positive=True):
                return super(InfiniteB,cls).__new__(cls, 1)
        self._do_compare_infinities(InfiniteB)
        self._do_comparisons(InfiniteB, B(35))