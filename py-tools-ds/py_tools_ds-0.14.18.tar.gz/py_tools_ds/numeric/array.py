# -*- coding: utf-8 -*-
__author__ = "Daniel Scheffler"

import numpy as np
from typing import List, Iterable  # noqa F401  # flake8 issue


def get_outFillZeroSaturated(dtype):
    """Returns the values for 'fill-', 'zero-' and 'saturated' pixels of an image
    to be written with regard to the target data type.

    :param dtype: data type of the image to be written
    """
    dtype = str(np.dtype(dtype))
    assert dtype in ['int8', 'uint8', 'int16', 'uint16', 'float32'], \
        "get_outFillZeroSaturated: Unknown dType: '%s'." % dtype
    dict_outFill = {'int8': -128, 'uint8': 0, 'int16': -9999, 'uint16': 9999, 'float32': -9999.}
    dict_outZero = {'int8': 0, 'uint8': 1, 'int16': 0, 'uint16': 1, 'float32': 0.}
    dict_outSaturated = {'int8': 127, 'uint8': 256, 'int16': 32767, 'uint16': 65535, 'float32': 65535.}
    return dict_outFill[dtype], dict_outZero[dtype], dict_outSaturated[dtype]


def get_array_tilebounds(array_shape, tile_shape):
    # type: (Iterable, Iterable) -> List[List[tuple]]
    """Calculate row/col bounds for image tiles according to the given parameters.

    :param array_shape:    dimensions of array to be tiled: (rows, columns, bands) or (rows, columns)
    :param tile_shape:     dimensions of target tile: (rows, columns, bands) or (rows, columns)
    """
    rows, cols = array_shape[:2]
    tgt_rows, tgt_cols = tile_shape[:2]
    tgt_rows, tgt_cols = tgt_rows or rows, tgt_cols or cols  # return all rows/cols in case tile_shape contains None

    row_bounds = [0]
    while row_bounds[-1] + tgt_rows < rows:
        row_bounds.append(row_bounds[-1] + tgt_rows - 1)
        row_bounds.append(row_bounds[-2] + tgt_rows)
    else:
        row_bounds.append(rows - 1)

    col_bounds = [0]
    while col_bounds[-1] + tgt_cols < cols:
        col_bounds.append(col_bounds[-1] + tgt_cols - 1)
        col_bounds.append(col_bounds[-2] + tgt_cols)
    else:
        col_bounds.append(cols - 1)

    return [[tuple([row_bounds[r], row_bounds[r + 1]]), tuple([col_bounds[c], col_bounds[c + 1]])]
            for r in range(0, len(row_bounds), 2) for c in range(0, len(col_bounds), 2)]
