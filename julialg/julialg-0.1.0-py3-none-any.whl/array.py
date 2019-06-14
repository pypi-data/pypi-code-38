"""Array utilities for abiding Julia-syntax in python
"""


import numpy


from julialg.core import JulialgError
from julialg.formatting import array_repr


def one_to_zero_index(x):
    if isinstance(x, slice):
        adjust = lambda x, attr: None if getattr(x, attr) is None else getattr(x, attr) - 1
        return slice(adjust(x, 'start'), adjust(x, 'stop'), x.step)
    elif isinstance(x, int):
        return x - 1
    else:
        raise JulialgError('Unable to convert item {} of type {} from one to zero index'.format(x, type(x)))




class JulArray:
    """A JulArray wraps a numpy ndarray mimicking some behavior of Julia LinearAlgebra package. Specifically,
    the JulArray is 1-indexed instead of 0-indexed, and is able to represent itself as a compact string
    similar to the Julia array representation.
    """

    def __init__(self, a: numpy.ndarray):
        """Create a JulArray

        Args:
            a:
                numpy.ndarray, the array to convert into Julia syntax
        """
        self._array = a

    def __getitem__(self, item):
        """Slice the array in a 1-indexed manner
        
        Args:
            item: 
                tuple or int, the indices along which to slice

        Returns:
            JulArray, with the underlying array sliced 
        """
        if isinstance(item, tuple):
            new_item = tuple(one_to_zero_index(x) for x in item)
        else:
            raise JulialgError('Unable to convert item {} of type {} to zero index format'.format(item, type(item)))
        return JulArray(self._array.__getitem__(new_item))

    def __repr__(self):
        """Represent the array as a compact string

        Returns:
            str
        """
        
        return array_repr(self._array) # todo fix to make like Julia

    @property
    def array(self):
        return self._array
