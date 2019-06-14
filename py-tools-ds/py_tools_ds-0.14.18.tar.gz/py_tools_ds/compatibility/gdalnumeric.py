# -*- coding: utf-8 -*-
__author__ = "Daniel Scheffler"

try:
    from osgeo import gdal
    from osgeo import gdalnumeric
except ImportError:
    import gdal
    import gdalnumeric  # FIXME this will import this __module__


def OpenNumPyArray(array):
    """This function emulates the functionality of gdalnumeric.OpenNumPyArray() which is not available in GDAL versions
     below 2.1.0 (?).

    :param array:   <numpy.ndarray> in the shape (bands, rows, columns)
    :return:
    """
    if array.ndim == 2:
        rows, cols = array.shape
        bands = 1
    elif array.ndim == 3:
        bands, rows, cols = array.shape
    else:
        raise ValueError('OpenNumPyArray() currently only supports 2D and 3D arrays. Given array shape is %s.'
                         % str(array.shape))

    # get output datatype
    gdal_dtype = gdalnumeric.NumericTypeCodeToGDALTypeCode(array.dtype)  # FIXME not all datatypes can be translated
    assert gdal_dtype is not None, 'Datatype %s is currently not supported by OpenNumPyArray().' % array.dtype

    mem_drv = gdal.GetDriverByName('MEM')
    mem_ds = mem_drv.Create('/vsimem/tmp/memfile.mem', cols, rows, bands, gdal_dtype)

    if mem_ds is None:
        raise Exception(gdal.GetLastErrorMsg())

    for bandNr in range(bands):
        band = mem_ds.GetRasterBand(bandNr + 1)
        band.WriteArray(array[:, :, bandNr] if bands > 1 else array)
        del band

    mem_ds.FlushCache()  # Write to disk.
    return mem_ds


def get_gdalnumeric_func(funcName):
    try:
        return getattr(gdalnumeric, funcName)
    except AttributeError:
        if funcName in globals():
            return globals()[funcName]
        else:
            raise AttributeError("'gdalnumeric' has no attribute '%s'." % funcName)
