# -*- coding: utf-8 -*-
# Copyright 2006 St James Software

"""Really simple dimension for wrapping a dictionary of resources."""

from j5test.IterativeTester import Dimension

class DictDim(Dimension):
    """A *really* simple dimension object for iterating over a dictionary.
       The keys of the dictionary given to __init__ are the resource names,
       the values are the resources.
       """

    def __init__(self,dct):
        self._resources = dct.copy()
