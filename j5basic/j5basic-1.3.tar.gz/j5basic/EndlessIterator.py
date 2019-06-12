# -*- coding: utf-8 -*-

"""Provides a generator which takes a list and repeats teh list endlessly"""

def EndlessIterator(baselist):
    while True:
        for item in baselist:
            yield item


