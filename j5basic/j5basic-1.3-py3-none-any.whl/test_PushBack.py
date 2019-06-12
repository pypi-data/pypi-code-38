#!/usr/bin/env python

from j5basic import PushBack

class TestPushBack:
    def test_wrap(self):
        i = [1,2,3,4,5]
        g = PushBack.PushBack(i.__iter__())
        l = list(g)
        assert i == l
    def test_simplepush(self):
        i = [1,2,3,4,5]
        g = PushBack.PushBack(i.__iter__())
        g.pushback(6)
        l = list(g)
        assert l == [6,1,2,3,4,5]
    def test_multipush(self):
        i = [1,2,3,4,5]
        g = PushBack.PushBack(i.__iter__())
        g.pushback(6)
        assert next(g) == 6
        assert next(g) == 1
        g.pushback(7)
        assert next(g) == 7
        l = list(g)
        assert l == [2,3,4,5]
        g.pushback(8)
        l = list(g)
        assert l == [8]
        l = list(g)
        assert l == []

class TestPushToBack:
    def test_wrap(self):
        i = [1,2,3,4,5]
        g = PushBack.PushToBack(i.__iter__())
        l = list(g)
        assert i == l

    def test_simplepush(self):
        i = [1,2,3,4,5]
        g = PushBack.PushToBack(i.__iter__())
        g.pushback(6)
        l = list(g)
        assert l == [1,2,3,4,5,6]

    def test_multipush(self):
        i = [1,2,3,4,5]
        g = PushBack.PushToBack(i.__iter__())
        g.pushback(6)
        assert next(g) == 1
        g.pushback(7)
        assert next(g) == 2
        l = list(g)
        assert l == [3,4,5,6,7]
        g.pushback(8)
        l = list(g)
        assert l == [8]
        l = list(g)
        assert l == []

