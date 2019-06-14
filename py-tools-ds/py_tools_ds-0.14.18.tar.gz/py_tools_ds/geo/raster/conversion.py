# -*- coding: utf-8 -*-
__author__ = "Daniel Scheffler"

from six import PY3

from shapely.wkb import loads
import numpy as np
from skimage.transform import rescale

try:
    import gdal
    import ogr
    import osr
except ImportError:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr

from ...io.raster.gdal import get_GDAL_ds_inmem
from ...processing.progress_mon import ProgressBar, Timer
from ...compatibility.python.exceptions import TimeoutError as TimeoutError_comp


def raster2polygon(array, gt, prj, DN2extract=1, exact=True, maxfeatCount=None,
                   timeout=None, progress=True, q=False):
    """Calculates a footprint polygon for the given array.

    :param array:             2D numpy array
    :param gt:
    :param prj:
    :param DN2extract:        <int, float> pixel value to create polygons for
    :param exact:
    :param maxfeatCount:      <int> the maximum expected number of polygons. If more polygons are found, every further
                              processing is cancelled and a RunTimeError is raised.
    :param timeout:           breaks the process after a given time in seconds
    :param progress:          show progress bars (default: True)
    :param q:                 quiet mode (default: False)
    :return:
    """

    assert array.ndim == 2, "Only 2D arrays are supported. Got a %sD array." % array.ndim

    # downsample input array in case is has more than 1e8 pixels to prevent crash
    if not exact and array.size > 1e8:  # 10000 x 10000 px
        zoom_factor = 0.5

        # downsample to half size, nearest neighbour
        array = rescale(array, zoom_factor, order=0, preserve_range=True, mode='edge').astype(np.bool)

        # update pixel sizes within gt
        gt = list(gt)
        gt[1] /= zoom_factor
        gt[5] /= zoom_factor

    src_ds = get_GDAL_ds_inmem(array, gt, prj)
    src_band = src_ds.GetRasterBand(1)

    # Create a memory OGR datasource to put results in.
    mem_drv = ogr.GetDriverByName('Memory')
    mem_ds = mem_drv.CreateDataSource('out')

    srs = osr.SpatialReference()
    srs.ImportFromWkt(prj)

    mem_layer = mem_ds.CreateLayer('poly', srs, ogr.wkbPolygon)

    fd = ogr.FieldDefn('DN', ogr.OFTInteger)
    mem_layer.CreateField(fd)

    # set callback
    callback = ProgressBar(prefix='Polygonize progress    ', suffix='Complete', barLength=50, timeout=timeout,
                           use_as_callback=True) \
        if progress and not q else Timer(timeout, use_as_callback=True) if timeout else None

    # run the algorithm
    status = gdal.Polygonize(src_band, src_band.GetMaskBand(), mem_layer, 0, ["8CONNECTED=8"] if exact else [],
                             callback=callback)

    # handle exit status other than 0 (fail)
    if status != 0:
        errMsg = gdal.GetLastErrorMsg()
        if errMsg == 'User terminated':
            raise TimeoutError('raster2polygon timed out!') if PY3 else TimeoutError_comp('raster2polygon timed out!')
        raise Exception(errMsg)

    # extract polygon
    mem_layer.SetAttributeFilter('DN = %s' % DN2extract)

    from geopandas import GeoDataFrame
    featCount = mem_layer.GetFeatureCount()

    if not featCount:
        raise RuntimeError('No features with DN=%s found in the input image.' % DN2extract)
    if maxfeatCount and featCount > maxfeatCount:
        raise RuntimeError('Found %s features with DN=%s but maximum feature count was set to %s.'
                           % (featCount, DN2extract, maxfeatCount))

    # tmp = np.full((featCount,2), DN, geoArr.dtype)
    # tmp[:,0] = range(featCount)
    # GDF = GeoDataFrame(tmp, columns=['idx','DN'])

    # def get_shplyPoly(GDF_row):
    #    if not is_timed_out(3):
    #        element   = mem_layer.GetNextFeature()
    #        shplyPoly = loads(element.GetGeometryRef().ExportToWkb()).buffer(0)
    #        element   = None
    #        return shplyPoly
    #    else:
    #        raise TimeoutError

    # GDF['geometry'] = GDF.apply(get_shplyPoly, axis=1)

    GDF = GeoDataFrame(columns=['geometry', 'DN'])
    timer = Timer(timeout)
    for i in range(featCount):
        if not timer.timed_out:
            element = mem_layer.GetNextFeature()
            GDF.loc[i] = [loads(element.GetGeometryRef().ExportToWkb()).buffer(0), DN2extract]
            del element
        else:
            raise TimeoutError('raster2polygon timed out!') if PY3 else TimeoutError_comp('raster2polygon timed out!')

    GDF = GDF.dissolve(by='DN')

    del mem_ds, mem_layer

    shplyPoly = GDF.loc[1, 'geometry']
    return shplyPoly
