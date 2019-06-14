# -*- coding: utf-8 -*-

import multiprocessing
import ctypes
import numpy as np


try:
    import gdal
except ImportError:
    from osgeo import gdal

from ...numeric.array import get_array_tilebounds

__author__ = "Daniel Scheffler"


shared_array = None


def init_SharedArray_in_globals(dims):
    rows, cols = dims
    global shared_array
    shared_array_base = multiprocessing.Array(ctypes.c_double, rows * cols)
    shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
    shared_array = shared_array.reshape(rows, cols)


def fill_arr(argDict, def_param=shared_array):
    pos = argDict.get('pos')
    func = argDict.get('func2call')
    args = argDict.get('func_args', [])
    kwargs = argDict.get('func_kwargs', {})

    (rS, rE), (cS, cE) = pos
    shared_array[rS:rE + 1, cS:cE + 1] = func(*args, **kwargs)


def gdal_read_subset(fPath, pos, bandNr):
    (rS, rE), (cS, cE) = pos
    ds = gdal.Open(fPath)
    data = ds.GetRasterBand(bandNr).ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
    del ds
    return data


def gdal_ReadAsArray_mp(fPath, bandNr, tilesize=1500):
    ds = gdal.Open(fPath)
    rows, cols = ds.RasterYSize, ds.RasterXSize
    del ds

    init_SharedArray_in_globals((rows, cols))

    tilepos = get_array_tilebounds(array_shape=(rows, cols), tile_shape=[tilesize, tilesize])
    fill_arr_argDicts = [{'pos': pos, 'func2call': gdal_read_subset, 'func_args': (fPath, pos, bandNr)} for pos in
                         tilepos]

    with multiprocessing.Pool() as pool:
        pool.map(fill_arr, fill_arr_argDicts)

    return shared_array
