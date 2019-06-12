# -*- coding: utf-8 -*-

from j5basic import EndlessIterator

def test_endless_iterator():
    it = EndlessIterator.EndlessIterator([0,1,2,3,4,5])
    for i in range(18):
        n = next(it)
        assert n == i % 6
