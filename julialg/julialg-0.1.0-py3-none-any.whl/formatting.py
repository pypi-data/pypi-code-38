"""Utilities for displaying arrays in a style similar to Julia"""
import itertools

import numpy

from julialg import core


@numpy.vectorize
def format_float(x: float, max_width: int = 8, precision: int = 4) -> str:
    """Format a float into a string

    Args:
        x: 
            float, a float to be formatted into string
        max_width:
            int, default 8, max width of each number in characters
        precision: 
            int, default 6, the number of decimals to use when formatting

    Returns:
        str
        >>> format_float([1.123456789])
        '1.123457'

        >>> format_float([1.123456789], precision=4)
        '1.1235'
    """
    fmt_string = '{{:>{}.{}f}}'.format(max_width, precision)
    return fmt_string.format(x)


def array_repr(array: numpy.ndarray, sliced_coords: tuple = None, max_cols: int = 15, max_rows: int = None,
               spacing: int = 3, precision: int = 4) -> str:
    """Convert an array to a 

    Args:
        array: 
            numpy.ndarray, the array to format nicely
        sliced_coords: 
            tuple[int], tuple of fixed indices 
        max_cols: 
            int, default 15
        max_rows: 
            int, default None
        spacing: 
            int, default 3
        precision: 
            int, default 6

    Returns:
        str
    """
    if sliced_coords is None:
        header = '{shape} Array{{{dtype},{ndim}}}'.format(shape='x'.join(str(i) for i in array.shape), dtype=array.dtype,
                                                          ndim=array.ndim)
    else:
        header = '[:, :, {}] = '.format(', '.join(str(i) for i in sliced_coords))

    if array.ndim > 2: # Julia only prints matrices, we need to slice
        body = '\n'.join(array_repr(array[(slice(None), slice(None)) + coords], coords, max_cols, max_rows, spacing, precision) for coords in
                           itertools.product(*(range(n) for n in array.shape[2:])))
    else: # we have a matrix, need to apply our condensing rules
        # First apply our coercion precision
        if array.dtype.kind == 'f':
            array = format_float(array, precision=precision)
        elif array.dtype.kind == 'i':
            array = array.astype(str)
        else:
            raise core.JulialgError('Unable to format matrix of kind: {}'.format(array.dtype.kind))

        # Apply our "condensing" rules
        # if array.shape[1] > max_rows:
        
        body = '\n'.join((spacing * ' ').join(array[:, n]) for n in range(array.shape[1])) + '\n'
        
    return '{header}\n{body}'.format(header=header, body=body)
