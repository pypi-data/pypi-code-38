# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 21:55:45 2019

@author: yoelr
"""
import numpy as np

__all__ = ('tuple_array',)

ndarray = np.ndarray
asarray = np.asarray

def invalid_method(self, *args, **kwargs):
    raise TypeError(f"'{type(self).__name__}' objects are immutable.")

class tuple_array(ndarray):
    """Create an array that is immutable and hashable.

    **Parameters**

         **array:** [array_like] Input data, in any form that can be converted to an array. This includes lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays.
         
         **dtype:** [data-type] By default, the data-type is inferred from the input data.
         
         **order:** {'C', 'F'} Whether to use row-major (C-style) or column-major (Fortran-style) memory representation. Defaults to ‘C’.

    **Examples**
    
        Create a tuple_array object:
            
        .. code-block:: python
    
            >>> arr = tuple_array([1, 18])
            tuple_array([1, 18])
            
        tuple_array objects are immutable:
            
            >>> arr[1] = 0
            TypeError: 'tuple_array' objects are immutable.
            
        tuple_array objects are hashable:
            
            >>> hash(arr)
            3713080549427813581
    
    """
    __slots__ = ()
    
    def __new__(cls, arr, dtype=np.float64, order='C'):
        self = asarray(arr, dtype, order).view(cls)
        return self
    
    def __hash__(self):
        return hash((tuple(self)))

    def __setitem__(self, key, val):
        raise TypeError(f"'{type(self).__name__}' objects are immutable.")

    def __array_wrap__(self, out_arr):
        # New array should not be a tuple_array
        if self is out_arr: return out_arr
        else: return out_arr.view(ndarray)
    
    def __repr__(self):
        Type = type(self).__name__
        rep = repr(asarray(self)).replace('array', Type)
        spaces = len(Type)*' '
        return rep.replace('\n     ', '\n' + spaces)
    
    __iadd__ = __isub__ = __imul__ = __imatmul__ = __itruediv__ = __idiv__ = __ifloordiv__ = __imod__ = __ipow__ = __ilshift__ = __irshift__ = __iand__ = __ixor__ = __ior__ = invalid_method



