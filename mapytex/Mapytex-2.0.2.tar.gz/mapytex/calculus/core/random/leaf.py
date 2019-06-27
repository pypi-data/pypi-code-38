#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""

"""
from ..coroutine import *


@coroutine
def look_for_rdleaf(target):
    """ Coroutine which look to "{...}" which are RdLeaf

    :example:
    >>> from ..str2 import list_sink
    >>> str2list = look_for_rdleaf(list_sink)
    >>> for i in "{a}+{a*b}-2":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> a
    [<RdLeaf a>, '+', <RdLeaf a*b>, '-', '2']

    """
    try:
        target_ = target()
    except TypeError:
        target_ = target

    stacking = False
    try:
        while True:
            tok = yield
            if tok == "{":
                stack = ""
                stacking = True
            elif tok == "}":
                target_.send(RdLeaf(stack))
                stack = ""
                stacking = False
            else:
                if stacking:
                    stack += tok
                else:
                    target_.send(tok)

    except STOOOP as err:
        yield target_.throw(err)


class RdLeaf:
    """ Random leaf

    """

    def __init__(self, name):
        self._name = name
        self.rdleaf = True

    @property
    def name(self):
        return self._name

    def replace(self, computed):
        return computed[self._name]

    def __str__(self):
        return "{" + self._name + "}"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._name}>"
