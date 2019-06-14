# -*- coding: utf-8 -*-
__author__ = "Daniel Scheffler"

import time
import os

import numpy as np
from pandas import DataFrame
from osgeo import gdal_array

try:
    from osgeo import gdal
except ImportError:
    import gdal  # FIXME this will import this __module__

from ...dtypes.conversion import dTypeDic_NumPy2GDALcompatible
from ...compatibility.gdalnumeric import get_gdalnumeric_func


def get_GDAL_ds_inmem(array, gt=None, prj=None, nodata=None):
    """Convert a numpy array into a GDAL dataset.
    NOTE: Possibly the data type has to be automatically changed in order ensure GDAL compatibility!

    :param array:   <numpy.ndarray> in the shape (rows, columns, bands)
    :param gt:
    :param prj:
    :param nodata:  <int> nodata value to be set (GDAL seems to have issues with non-int nodata values.)
    :return:
    """
    # FIXME does not respect different nodata values for each band

    if len(array.shape) == 3:
        array = np.rollaxis(array, 2)  # rows,cols,bands => bands,rows,cols

    # convert data type to GDAL compatible data type
    if gdal_array.NumericTypeCodeToGDALTypeCode(array.dtype) is None:
        array = array.astype(dTypeDic_NumPy2GDALcompatible[str(np.dtype(array.dtype))])

    OpenNumPyArray = get_gdalnumeric_func('OpenArray')
    ds = OpenNumPyArray(array)

    if ds is None:
        raise Exception(gdal.GetLastErrorMsg())
    if gt:
        ds.SetGeoTransform(gt)
    if prj:
        ds.SetProjection(prj)

    if nodata is not None:
        for i in range(ds.RasterCount):
            band = ds.GetRasterBand(i + 1)
            try:
                band.SetNoDataValue(nodata)
            except TypeError:
                raise TypeError(type(nodata), 'TypeError while trying to set NoDataValue to %s. ' % nodata)
            del band

    ds.FlushCache()  # Write to disk.
    return ds


def get_GDAL_driverList():
    count = gdal.GetDriverCount()
    df = DataFrame(np.full((count, 5), np.nan), columns=['drvCode', 'drvLongName', 'ext1', 'ext2', 'ext3'])
    for i in range(count):
        drv = gdal.GetDriver(i)
        if drv.GetMetadataItem(gdal.DCAP_RASTER):
            meta = drv.GetMetadataItem(gdal.DMD_EXTENSIONS)
            extensions = meta.split() if meta else []
            df.ix[i] = [drv.GetDescription(),
                        drv.GetMetadataItem(gdal.DMD_LONGNAME),
                        extensions[0] if len(extensions) > 0 else np.nan,
                        extensions[1] if len(extensions) > 1 else np.nan,
                        extensions[2] if len(extensions) > 2 else np.nan]
    df = df.dropna(how='all')
    return df


def wait_if_used(path_file, lockfile, timeout=100, try_kill=0):
    globs = globals()
    same_gdalRefs = [k for k, v in globs.items() if
                     isinstance(globs[k], gdal.Dataset) and globs[k].GetDescription() == path_file]
    t0 = time.time()

    def update_same_gdalRefs(sRs):
        return [sR for sR in sRs if sR in globals() and globals()[sR] is not None]

    while same_gdalRefs != [] or os.path.exists(lockfile):
        if os.path.exists(lockfile):
            continue

        if time.time() - t0 > timeout:
            if try_kill:
                for sR in same_gdalRefs:
                    globals()[sR] = None
                    print('had to kill %s' % sR)
            else:
                if os.path.exists(lockfile):
                    os.remove(lockfile)

                raise TimeoutError('The file %s is permanently used by another variable.' % path_file)

        same_gdalRefs = update_same_gdalRefs(same_gdalRefs)
