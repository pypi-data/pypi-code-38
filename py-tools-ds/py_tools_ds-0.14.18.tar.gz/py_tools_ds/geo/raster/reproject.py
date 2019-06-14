# -*- coding: utf-8 -*-
import numpy as np
import warnings
import multiprocessing
import os
from tempfile import TemporaryDirectory
from typing import Union, Tuple, List, Any  # noqa: F401
import sys

# custom
try:
    from osgeo import gdal
    from osgeo import gdalnumeric
except ImportError:
    import gdal
    import gdalnumeric


# NOTE: In case of ImportError: dlopen: cannot load any more object with static TLS,
#       one could add 'from pykdtree.kdtree import KDTree' here (before pyresample import)
from pyresample.geometry import AreaDefinition, SwathDefinition
from pyresample.bilinear import resample_bilinear
from pyresample.kd_tree import resample_nearest, resample_gauss, resample_custom

from ...dtypes.conversion import dTypeDic_NumPy2GDAL
from ..projection import EPSG2WKT, WKT2EPSG, isProjectedOrGeographic, prj_equal, proj4_to_WKT
from ..coord_trafo import pixelToLatLon, get_proj4info, proj4_to_dict, transform_coordArray, transform_any_prj
from ..coord_calc import corner_coord_to_minmax, get_corner_coordinates
from ...io.raster.gdal import get_GDAL_ds_inmem
from ...io.raster.writer import write_numpy_to_image
from ...processing.progress_mon import ProgressBar
from ...compatibility.gdal import get_gdal_func
from ...processing.shell import subcall_with_output

__author__ = "Daniel Scheffler"


def warp_ndarray_OLD(ndarray, in_gt, in_prj, out_prj, out_gt=None, outRowsCols=None, outUL=None, out_res=None,
                     out_extent=None, out_dtype=None, rsp_alg=0, in_nodata=None, out_nodata=None,
                     outExtent_within=True):  # pragma: no cover
    """Reproject / warp a numpy array with given geo information to target coordinate system.

    :param ndarray:             numpy.ndarray [rows,cols,bands]
    :param in_gt:               input gdal GeoTransform
    :param in_prj:              input projection as WKT string
    :param out_prj:             output projection as WKT string
    :param out_gt:              output gdal GeoTransform as float tuple in the source coordinate system (optional)
    :param outUL:               [X,Y] output upper left coordinates as floats in the source coordinate system
                                (requires outRowsCols)
    :param outRowsCols:         [rows, cols] (optional)
    :param out_res:             output resolution as tuple of floats (x,y) in the TARGET coordinate system
    :param out_extent:          [left, bottom, right, top] as floats in the source coordinate system
    :param out_dtype:           output data type as numpy data type
    :param rsp_alg:             Resampling method to use. One of the following (int, default is 0):
                                0 = nearest neighbour, 1 = bilinear, 2 = cubic, 3 = cubic spline, 4 = lanczos,
                                5 = average, 6 = mode
    :param in_nodata:           no data value of the input image
    :param out_nodata:          no data value of the output image
    :param outExtent_within:    Ensures that the output extent is within the input extent.
                                Otherwise an exception is raised.
    :return out_arr:            warped numpy array
    :return out_gt:             warped gdal GeoTransform
    :return out_prj:            warped projection as WKT string
    """
    # NOTE: rasterio seems to increase the number of objects with static TLS
    #       There is a maximum number and if this is exceeded an ImportError is raised:
    #       ImportError: dlopen: cannot load any more object with static TLS
    #       - see also: https://gitext.gfz-potsdam.de/danschef/py_tools_ds/issues/8
    #       - NOTE: importing rasterio AFTER pyresample (which uses pykdtree) seems to solve that too
    #       => keep the rasterio import within the function locals to avoid not needed imports
    import rasterio
    from rasterio.warp import reproject as rio_reproject
    from rasterio.warp import calculate_default_transform as rio_calc_transform
    from rasterio.warp import Resampling

    if not ndarray.flags['OWNDATA']:
        temp = np.empty_like(ndarray)
        temp[:] = ndarray
        ndarray = temp  # deep copy: converts view to its own array in order to avoid wrong output

    with rasterio.env.Env():
        if outUL is not None:
            assert outRowsCols is not None, 'outRowsCols must be given if outUL is given.'
        outUL = [in_gt[0], in_gt[3]] if outUL is None else outUL

        inEPSG, outEPSG = [WKT2EPSG(prj) for prj in [in_prj, out_prj]]
        assert inEPSG, 'Could not derive input EPSG code.'
        assert outEPSG, 'Could not derive output EPSG code.'
        assert in_nodata is None or isinstance(in_nodata, (int, float)), \
            'Received invalid input nodata value: %s; type: %s.' % (in_nodata, type(in_nodata))
        assert out_nodata is None or isinstance(out_nodata, (int, float)), \
            'Received invalid output nodata value: %s; type: %s.' % (out_nodata, type(out_nodata))

        src_crs = {'init': 'EPSG:%s' % inEPSG}
        dst_crs = {'init': 'EPSG:%s' % outEPSG}

        if len(ndarray.shape) == 3:
            # convert input array axis order to rasterio axis order
            ndarray = np.swapaxes(np.swapaxes(ndarray, 0, 2), 1, 2)
            bands, rows, cols = ndarray.shape
            rows, cols = outRowsCols if outRowsCols else (rows, cols)
        else:
            rows, cols = ndarray.shape if outRowsCols is None else outRowsCols

        # set dtypes ensuring at least int16 (int8 is not supported by rasterio)
        in_dtype = ndarray.dtype
        out_dtype = ndarray.dtype if out_dtype is None else out_dtype
        out_dtype = np.int16 if str(out_dtype) == 'int8' else out_dtype
        ndarray = ndarray.astype(np.int16) if str(in_dtype) == 'int8' else ndarray

        # get dst_transform
        def gt2bounds(gt, r, c): return [gt[0], gt[3] + r * gt[5], gt[0] + c * gt[1], gt[3]]  # left, bottom, right, top

        if out_gt is None and out_extent is None:
            if outRowsCols:
                outUL = [in_gt[0], in_gt[3]] if outUL is None else outUL

                def ulRC2bounds(ul, r, c):
                    return [ul[0], ul[1] + r * in_gt[5], ul[0] + c * in_gt[1], ul[1]]  # left, bottom, right, top

                left, bottom, right, top = ulRC2bounds(outUL, rows, cols)

            else:  # outRowsCols is None and outUL is None: use in_gt
                left, bottom, right, top = gt2bounds(in_gt, rows, cols)
                # ,im_xmax,im_ymin,im_ymax = corner_coord_to_minmax(get_corner_coordinates(self.ds_im2shift))

        elif out_extent:
            left, bottom, right, top = out_extent

        else:  # out_gt is given
            left, bottom, right, top = gt2bounds(in_gt, rows, cols)

        if outExtent_within:
            # input array is only a window of the actual input array
            assert left >= in_gt[0] and right <= (in_gt[0] + (cols + 1) * in_gt[1]) and \
                   bottom >= in_gt[3] + (rows + 1) * in_gt[5] and top <= in_gt[3], \
                   "out_extent has to be completely within the input image bounds."

        if out_res is None:
            # get pixel resolution in target coord system
            prj_in_out = (isProjectedOrGeographic(in_prj), isProjectedOrGeographic(out_prj))
            assert None not in prj_in_out, 'prj_in_out contains None.'

            if prj_in_out[0] == prj_in_out[1]:
                out_res = (in_gt[1], abs(in_gt[5]))

            elif prj_in_out == ('geographic', 'projected'):
                raise NotImplementedError('Different projections are currently not supported.')

            else:  # ('projected','geographic')
                px_size_LatLon = np.array(pixelToLatLon([1, 1], geotransform=in_gt, projection=in_prj)) - \
                                 np.array(pixelToLatLon([0, 0], geotransform=in_gt, projection=in_prj))
                out_res = tuple(reversed(abs(px_size_LatLon)))
                print('OUT_RES NOCHMAL CHECKEN: ', out_res)

        dict_rspInt_rspAlg = \
            {0: Resampling.nearest, 1: Resampling.bilinear, 2: Resampling.cubic,
             3: Resampling.cubic_spline, 4: Resampling.lanczos, 5: Resampling.average, 6: Resampling.mode}

        var1 = True
        if var1:
            src_transform = rasterio.transform.from_origin(in_gt[0], in_gt[3], in_gt[1], abs(in_gt[5]))
            print('calc_trafo_args')
            for i in [src_crs, dst_crs, cols, rows, left, bottom, right, top, out_res]:
                print(i, '\n')
            left, right, bottom, top = corner_coord_to_minmax(get_corner_coordinates(gt=in_gt, rows=rows, cols=cols))

            dst_transform, out_cols, out_rows = rio_calc_transform(
                src_crs, dst_crs, cols, rows, left, bottom, right, top, resolution=out_res)

            out_arr = np.zeros((bands, out_rows, out_cols), out_dtype) \
                if len(ndarray.shape) == 3 else np.zeros((out_rows, out_cols), out_dtype)
            print(out_res)
            for i in [src_transform, src_crs, dst_transform, dst_crs]:
                print(i, '\n')
            rio_reproject(ndarray, out_arr, src_transform=src_transform, src_crs=src_crs, dst_transform=dst_transform,
                          dst_crs=dst_crs, resampling=dict_rspInt_rspAlg[rsp_alg], src_nodata=in_nodata,
                          dst_nodata=out_nodata)

            aff = list(dst_transform)
            out_gt = out_gt if out_gt else (aff[2], aff[0], aff[1], aff[5], aff[3], aff[4])
            # FIXME sometimes output dimensions are not exactly as requested (1px difference)
        else:
            dst_transform, out_cols, out_rows = rio_calc_transform(
                src_crs, dst_crs, cols, rows, left, bottom, right, top, resolution=out_res)

            # check if calculated output dimensions correspond to expected ones and correct them if neccessary
            # rows_expected = int(round(abs(top - bottom) / out_res[1], 0))
            # cols_expected = int(round(abs(right - left) / out_res[0], 0))

            # diff_rows_exp_real, diff_cols_exp_real = abs(out_rows - rows_expected), abs(out_cols - cols_expected)
            # if diff_rows_exp_real > 0.1 or diff_cols_exp_real > 0.1:
            # assert diff_rows_exp_real < 1.1 and diff_cols_exp_real < 1.1,
            #     'warp_ndarray: The output image size calculated by rasterio is too far away from the expected output '
            #     'image size.'
            #    out_rows, out_cols = rows_expected, cols_expected
            # fixes an issue where rio_calc_transform() does not return quadratic output image although input parameters
            # correspond to a quadratic image and inEPSG equals outEPSG

            aff = list(dst_transform)
            out_gt = out_gt if out_gt else (aff[2], aff[0], aff[1], aff[5], aff[3], aff[4])

            out_arr = np.zeros((bands, out_rows, out_cols), out_dtype) \
                if len(ndarray.shape) == 3 else np.zeros((out_rows, out_cols), out_dtype)

            with warnings.catch_warnings():
                # FIXME supresses: FutureWarning:
                # FIXME: GDAL-style transforms are deprecated and will not be supported in Rasterio 1.0.
                warnings.simplefilter('ignore')
                try:
                    # print('INPUTS')
                    # print(ndarray.shape, ndarray.dtype, out_arr.shape, out_arr.dtype)
                    # print(in_gt)
                    # print(src_crs)
                    # print(out_gt)
                    # print(dst_crs)
                    # print(dict_rspInt_rspAlg[rsp_alg])
                    # print(in_nodata)
                    # print(out_nodata)
                    for i in [in_gt, src_crs, out_gt, dst_crs]:
                        print(i, '\n')
                    rio_reproject(ndarray, out_arr,
                                  src_transform=in_gt, src_crs=src_crs, dst_transform=out_gt, dst_crs=dst_crs,
                                  resampling=dict_rspInt_rspAlg[rsp_alg], src_nodata=in_nodata, dst_nodata=out_nodata)
                    # from matplotlib import pyplot as plt
                    # print(out_arr.shape)
                    # plt.figure()
                    # plt.imshow(out_arr[:,:,1])
                except KeyError:
                    print(in_dtype, str(in_dtype))
                    print(ndarray.dtype)

        # convert output array axis order to GMS axis order [rows,cols,bands]
        out_arr = out_arr if len(ndarray.shape) == 2 else np.swapaxes(np.swapaxes(out_arr, 0, 1), 1, 2)

        if outRowsCols:
            out_arr = out_arr[:outRowsCols[0], :outRowsCols[1]]

    return out_arr, out_gt, out_prj


def warp_GeoArray(geoArr, **kwargs):  # pragma: no cover
    # TODO remove that function
    warnings.warn("warp_GeoArray is deprecated. Use geoarray.GeoArray.reproject_to_new_grid instead.",
                  DeprecationWarning)
    # FIXME this does not copy GeoArray attributes
    # ndarray = geoArr[:]
    # from geoarray import GeoArray
    # return GeoArray(*warp_ndarray(ndarray, geoArr.geotransform, geoArr.projection, **kwargs))


def warp_ndarray(ndarray, in_gt, in_prj=None, out_prj=None, out_dtype=None,
                 out_gsd=(None, None), out_bounds=None, out_bounds_prj=None, out_XYdims=(None, None),
                 rspAlg='near', in_nodata=None, out_nodata=None, in_alpha=False,
                 out_alpha=False, targetAlignedPixels=False, gcpList=None, polynomialOrder=None, options=None,
                 transformerOptions=None, warpOptions=None, CPUs=1, warpMemoryLimit=0, progress=True, q=False):
    # type: () -> (np.ndarray, tuple, str)
    """

    :param ndarray:             numpy array to be warped (or a list of numpy arrays (requires lists for in_gt/in_prj))
    :param in_gt:               input GDAL geotransform (or a list of GDAL geotransforms)
    :param in_prj:              input GDAL projection or list of projections (WKT string, 'EPSG:1234', <EPSG_int>),
                                default: "LOCAL_CS[\"MAP\"]"
    :param out_prj:             output GDAL projection (WKT string, 'EPSG:1234', <EPSG_int>),
                                default: "LOCAL_CS[\"MAP\"]"
    :param out_dtype:           gdal.DataType
    :param out_gsd:
    :param out_bounds:          [xmin,ymin,xmax,ymax] set georeferenced extents of output file to be created,
                                e.g. [440720, 3750120, 441920, 3751320])
                                (in target SRS by default, or in the SRS specified with -te_srs)
    :param out_bounds_prj:
    :param out_XYdims:
    :param rspAlg:              <str> Resampling method to use. Available methods are:
                                near, bilinear, cubic, cubicspline, lanczos, average, mode, max, min, med, q1, q2
    :param in_nodata:
    :param out_nodata:
    :param in_alpha:            <bool> Force the last band of a source image to be considered as a source alpha band.
    :param out_alpha:           <bool> Create an output alpha band to identify nodata (unset/transparent) pixels
    :param targetAlignedPixels:   (GDAL >= 1.8.0) (target aligned pixels) align the coordinates of the extent
                                        of the output file to the values of the -tr, such that the aligned extent
                                        includes the minimum extent.
    :param gcpList:             <list> list of ground control points in the output coordinate system
                                to be used for warping, e.g. [gdal.GCP(mapX,mapY,mapZ,column,row),...]
    :param polynomialOrder:     <int> order of polynomial GCP interpolation
    :param options:             <str> additional GDAL options as string, e.g. '-nosrcalpha' or '-order'
    :param transformerOptions:  <list> list of transformer options, e.g.  ['SRC_SRS=invalid']
    :param warpOptions:         <list> list of warp options, e.g.  ['CUTLINE_ALL_TOUCHED=TRUE'],
                                find available options here: http://www.gdal.org/structGDALWarpOptions.html
    :param CPUs:                <int> number of CPUs to use (default: None, which means 'all CPUs available')
    :param warpMemoryLimit:     <int> size of working buffer in bytes (default: 0)
    :param progress:            <bool> show progress bar (default: True)
    :param q:                   <bool> quiet mode (default: False)
    :return:

    """
    # TODO complete type hint
    # TODO test if this function delivers the exact same output like console version,
    # TODO otherwise implment error_threshold=0.125
    # how to implement:    https://svn.osgeo.org/gdal/trunk/autotest/utilities/test_gdalwarp_lib.py

    # assume local coordinates if no projections are given
    if not in_prj and not out_prj:
        if out_bounds_prj and not out_bounds_prj.startswith('LOCAL_CS'):
            raise ValueError("'out_bounds_prj' cannot have a projection if 'in_prj' and 'out_prj' are not given.")
        in_prj = out_prj = out_bounds_prj = "LOCAL_CS[\"MAP\"]"

    # assertions
    if rspAlg == 'average':
        is_avail_rsp_average = int(gdal.VersionInfo()[0]) >= 2
        if not is_avail_rsp_average:
            warnings.warn("The GDAL version on this machine does not yet support the resampling algorithm 'average'. "
                          "'cubic' is used instead. To avoid this please update GDAL to a version above 2.0.0!")
            rspAlg = 'cubic'

    if not isinstance(ndarray, (list, tuple)):
        assert str(np.dtype(ndarray.dtype)) in dTypeDic_NumPy2GDAL, "Unknown target datatype '%s'." % ndarray.dtype
    else:
        assert str(np.dtype(ndarray[0].dtype)) in dTypeDic_NumPy2GDAL, "Unknown target datatype '%s'." \
                                                                       % ndarray[0].dtype
        assert isinstance(in_gt, (list, tuple)), "If 'ndarray' is a list, 'in_gt' must also be a list!"
        assert isinstance(in_prj, (list, tuple)), "If 'ndarray' is a list, 'in_prj' must also be a list!"
        assert len(list(set([arr.dtype for arr in ndarray]))) == 1,  "Data types of input ndarray list must be equal."

    def get_SRS(prjArg):
        return prjArg if isinstance(prjArg, str) and prjArg.startswith('EPSG:') else \
            'EPSG:%s' % prjArg if isinstance(prjArg, int) else prjArg

    def get_GDT(DT): return dTypeDic_NumPy2GDAL[str(np.dtype(DT))]

    in_dtype_np = ndarray.dtype if not isinstance(ndarray, (list, tuple)) else ndarray[0].dtype

    # # not yet implemented
    # # TODO cutline from OGR datasource. => implement input shapefile or Geopandas dataframe
    # cutlineDSName = 'data/cutline.vrt'  # '/vsimem/cutline.shp'
    # cutlineLayer = 'cutline'
    # cropToCutline = False
    # cutlineSQL = 'SELECT * FROM cutline'
    # cutlineWhere = '1 = 1'
    # rpc = [
    #     "HEIGHT_OFF=1466.05894327379",
    #     "HEIGHT_SCALE=144.837606185489",
    #     "LAT_OFF=38.9266809014185",
    #     "LAT_SCALE=-0.108324009570885",
    #     "LINE_DEN_COEFF="
    #     "1 -0.000392404256440504 -0.0027925489381758 0.000501819414812054 0.00216726134806561 "
    #     "-0.00185617059201599 0.000183834173326118 -0.00290342803717354 -0.00207181007131322 -0.000900223247894285 "
    #     "-0.00132518281680544 0.00165598132063197 0.00681015244696305 0.000547865679631528 0.00516214646283021 "
    #     "0.00795287690785699 -0.000705040639059332 -0.00254360623317078 -0.000291154885056484 0.00070943440010757",
    #     "LINE_NUM_COEFF="
    #     "-0.000951099635749339 1.41709976082781 -0.939591985038569 -0.00186609235173885 0.00196881101098923 "
    #     "0.00361741523740639 -0.00282449434932066 0.0115361898794214 -0.00276027843825304 9.37913944402154e-05 "
    #     "-0.00160950221565737 0.00754053609977256 0.00461831968713819 0.00274991122620312 0.000689605203796422 "
    #     "-0.0042482778732957 -0.000123966494595151 0.00307976709897974 -0.000563274426174409 0.00049981716767074",
    #     "LINE_OFF=2199.50159296339",
    #     "LINE_SCALE=2195.852519621",
    #     "LONG_OFF=76.0381768085136",
    #     "LONG_SCALE=0.130066683772651",
    #     "SAMP_DEN_COEFF="
    #     "1 -0.000632078047521022 -0.000544107268758971 0.000172438016778527 -0.00206391734870399 "
    #     "-0.00204445747536872 -0.000715754551621987 -0.00195545265530244 -0.00168532972557267 -0.00114709980708329 "
    #     "-0.00699131177532728 0.0038551339822296 0.00283631282133365 -0.00436885468926666 -0.00381335885955994 "
    #     "0.0018742043611019 -0.0027263909314293 -0.00237054119407013 0.00246374716379501 -0.00121074576302219",
    #     "SAMP_NUM_COEFF="
    #     "0.00249293151551852 -0.581492592442025 -1.00947448466175 0.00121597346320039 -0.00552825219917498 "
    #     "-0.00194683170765094 -0.00166012459012905 -0.00338315804553888 -0.00152062885009498 -0.000214562164393127 "
    #     "-0.00219914905535387 -0.000662800177832777 -0.00118644828432841 -0.00180061222825708 -0.00364756875260519 "
    #     "-0.00287273485650089 -0.000540077934728493 -0.00166800463003749 0.000201057249109451 -8.49620129025469e-05",
    #     "SAMP_OFF=3300.34602166792",
    #     "SAMP_SCALE=3297.51222987611"
    # ]

    """ Create a WarpOptions() object that can be passed to gdal.Warp()
        Keyword arguments are :
          options --- can be be an array of strings, a string or let empty and filled from other keywords.
          format --- output format ("GTiff", etc...)
          outputBounds --- output bounds as (minX, minY, maxX, maxY) in target SRS
          outputBoundsSRS --- SRS in which output bounds are expressed, in the case they are not expressed in dstSRS
          xRes, yRes --- output resolution in target SRS
          targetAlignedPixels --- whether to force output bounds to be multiple of output resolution
          width --- width of the output raster in pixel
          height --- height of the output raster in pixel
          srcSRS --- source SRS
          dstSRS --- output SRS
          srcAlpha --- whether to force the last band of the input dataset to be considered as an alpha band
          dstAlpha --- whether to force the creation of an output alpha band
          outputType --- output type (gdal.GDT_Byte, etc...)
          workingType --- working type (gdal.GDT_Byte, etc...)
          warpOptions --- list of warping options
          errorThreshold --- error threshold for approximation transformer (in pixels)
          warpMemoryLimit --- size of working buffer in bytes
          resampleAlg --- resampling mode
          creationOptions --- list of creation options
          srcNodata --- source nodata value(s)
          dstNodata --- output nodata value(s)
          multithread --- whether to multithread computation and I/O operations
          tps --- whether to use Thin Plate Spline GCP transformer
          rpc --- whether to use RPC transformer
          geoloc --- whether to use GeoLocation array transformer
          polynomialOrder --- order of polynomial GCP interpolation
          transformerOptions --- list of transformer options
          cutlineDSName --- cutline dataset name
          cutlineLayer --- cutline layer name
          cutlineWhere --- cutline WHERE clause
          cutlineSQL --- cutline SQL statement
          cutlineBlend --- cutline blend distance in pixels
          cropToCutline --- whether to use cutline extent for output bounds
          copyMetadata --- whether to copy source metadata
          metadataConflictValue --- metadata data conflict value
          setColorInterpretation --- whether to force color interpretation of input bands to output bands
          callback --- callback method
          callback_data --- user data for callback  # value for last parameter of progress callback
    """

    # get input dataset (in-MEM)
    if not isinstance(ndarray, (list, tuple)):
        in_ds = get_GDAL_ds_inmem(ndarray, in_gt, in_prj)
    else:
        # list of ndarrays
        in_ds = [get_GDAL_ds_inmem(arr, gt, prj) for arr, gt, prj in zip(ndarray, in_gt, in_prj)]

    # set RPCs
    # if rpcList:
    #    in_ds.SetMetadata(rpc, "RPC")
    #    transformerOptions = ['RPC_DEM=data/warp_52_dem.tif']

    if CPUs is None or CPUs > 1:
        gdal.SetConfigOption('GDAL_NUM_THREADS', str(CPUs if CPUs else multiprocessing.cpu_count()))

        # gdal.SetConfigOption('GDAL_CACHEMAX', str(800))

        # GDAL Translate if needed
        # if gcpList:
        #   in_ds.SetGCPs(gcpList, in_ds.GetProjection())

    if gcpList:
        gdal_Translate = get_gdal_func('Translate')
        in_ds = gdal_Translate(
            '', in_ds, format='MEM',
            outputSRS=get_SRS(out_prj),
            GCPs=gcpList,
            callback=ProgressBar(prefix='Translating progress', timeout=None) if progress and not q else None
        )
        # NOTE: options = ['SPARSE_OK=YES'] ## => what is that for?

    # GDAL Warp
    gdal_Warp = get_gdal_func('Warp')
    res_ds = gdal_Warp(
        '', in_ds, format='MEM',
        dstSRS=get_SRS(out_prj),
        outputType=get_GDT(out_dtype) if out_dtype else get_GDT(in_dtype_np),
        xRes=out_gsd[0],
        yRes=out_gsd[1],
        outputBounds=out_bounds,
        outputBoundsSRS=get_SRS(out_bounds_prj),
        width=out_XYdims[0],
        height=out_XYdims[1],
        resampleAlg=rspAlg,
        srcNodata=in_nodata,
        dstNodata=out_nodata,
        srcAlpha=in_alpha,
        dstAlpha=out_alpha,
        options=options if options else [],
        warpOptions=warpOptions or [],
        transformerOptions=transformerOptions or [],
        targetAlignedPixels=targetAlignedPixels,
        tps=True if gcpList else False,
        polynomialOrder=polynomialOrder,
        warpMemoryLimit=warpMemoryLimit,
        callback=ProgressBar(prefix='Warping progress    ', timeout=None) if progress and not q else None,
        callback_data=[0],
        errorThreshold=0.125,  # this is needed to get exactly the same output like the console version of GDAL warp
    )

    gdal.SetConfigOption('GDAL_NUM_THREADS', None)

    if res_ds is None:
        raise Exception('Warping Error:  ' + gdal.GetLastErrorMsg())

    # get outputs
    res_arr = gdalnumeric.DatasetReadAsArray(res_ds)
    if len(res_arr.shape) == 3:
        res_arr = np.swapaxes(np.swapaxes(res_arr, 0, 2), 0, 1)

    res_gt = res_ds.GetGeoTransform()
    res_prj = res_ds.GetProjection()

    # cleanup
    del in_ds, res_ds

    # dtype check -> possibly dtype had to be changed for GDAL compatibility
    if in_dtype_np != res_arr.dtype:
        res_arr = res_arr.astype(in_dtype_np)

    # test output
    if out_prj and prj_equal(out_prj, 4626):
        assert -180 < res_gt[0] < 180 and -90 < res_gt[3] < 90, 'Testing of gdal_warp output failed.'

    # output bounds verification
    if out_bounds:
        xmin, xmax, ymin, ymax = \
            corner_coord_to_minmax(get_corner_coordinates(gt=res_gt, rows=res_arr.shape[0], cols=res_arr.shape[1]))
        if False in np.isclose(out_bounds, (xmin, ymin, xmax, ymax)):
            warnings.warn('The output bounds of warp_ndarray do not match the requested bounds!')

    return res_arr, res_gt, res_prj


class SensorMapGeometryTransformer(object):
    def __init__(self, lons, lats, resamp_alg='nearest', radius_of_influence=30, **opts):
        # type: (np.ndarray, np.ndarray, str, int, Any) -> None
        """Get an instance of SensorMapGeometryTransformer.

        :param lons:    2D longitude array corresponding to the 2D sensor geometry array
        :param lats:    2D latitude array corresponding to the 2D sensor geometry array

        :Keyword Arguments:  (further documentation here: https://pyresample.readthedocs.io/en/latest/swath.html)
            - resamp_alg:           resampling algorithm ('nearest', 'bilinear', 'gauss', 'custom')
            - radius_of_influence:  <float> Cut off distance in meters (default: 30)
                                    NOTE: keyword is named 'radius' in case of bilinear resampling
            - sigmas:               <list of floats or float> [ONLY 'gauss'] List of sigmas to use for the gauss
                                    weighting of each channel 1 to k, w_k = exp(-dist^2/sigma_k^2). If only one channel
                                    is resampled sigmas is a single float value.
            - neighbours:           <int> [ONLY 'bilinear', 'gauss'] Number of neighbours to consider for each grid
                                    point when searching the closest corner points
            - epsilon:              <float> Allowed uncertainty in meters. Increasing uncertainty reduces execution time
            - weight_funcs:         <list of function objects or function object> [ONLY 'custom'] List of weight
                                    functions f(dist) to use for the weighting of each channel 1 to k. If only one
                                    channel is resampled weight_funcs is a single function object.
            - fill_value:           <int or None> Set undetermined pixels to this value.
                                    If fill_value is None a masked array is returned with undetermined pixels masked
            - reduce_data:          <bool> Perform initial coarse reduction of source dataset in order to reduce
                                    execution time
            - nprocs:               <int>, Number of processor cores to be used
            - segments:             <int or None> Number of segments to use when resampling.
                                    If set to None an estimate will be calculated
            - with_uncert:          <bool> [ONLY 'gauss' and 'custom'] Calculate uncertainty estimates
                                    NOTE: resampling function has 3 return values instead of 1: result, stddev, count
        """
        # validation
        if lons.ndim != 2:
            raise ValueError('Expected a 2D longitude array. Received a %dD array.' % lons.ndim)
        if lats.ndim != 2:
            raise ValueError('Expected a 2D latitude array. Received a %dD array.' % lats.ndim)
        if lons.shape != lats.shape:
            raise ValueError((lons.shape, lats.shape), "'lons' and 'lats' are expected to have the same shape.")

        self.resamp_alg = resamp_alg
        self.opts = dict(radius_of_influence=radius_of_influence,
                         sigmas=(radius_of_influence / 2))
        self.opts.update(opts)

        if resamp_alg == 'bilinear':
            del self.opts['radius_of_influence']
            self.opts['radius'] = radius_of_influence

        # NOTE: If pykdtree is built with OpenMP support (default) the number of threads is controlled with the
        #       standard OpenMP environment variable OMP_NUM_THREADS. The nprocs argument has no effect on pykdtree.
        if 'nprocs' in self.opts:
            if self.opts['nprocs'] > 1:
                os.environ['OMP_NUM_THREADS'] = '%d' % opts['nprocs']
            del self.opts['nprocs']

        self.lats = lats
        self.lons = lons
        self.swath_definition = SwathDefinition(lons=lons, lats=lats)
        self.area_extent_ll = [np.min(lons), np.min(lats), np.max(lons), np.max(lats)]
        self.area_definition = None  # type: AreaDefinition

    def _get_target_extent(self, tgt_epsg):
        if tgt_epsg == 4326:
            tgt_extent = self.area_extent_ll
        else:
            corner_coords_ll = [[self.lons[0, 0], self.lats[0, 0]],  # UL_xy
                                [self.lons[0, -1], self.lats[0, -1]],  # UR_xy
                                [self.lons[-1, 0], self.lats[-1, 0]],  # LL_xy
                                [self.lons[-1, -1], self.lats[-1, -1]],  # LR_xy
                                ]
            corner_coords_tgt_prj = [transform_any_prj(EPSG2WKT(4326), EPSG2WKT(tgt_epsg), x, y)
                                     for x, y in corner_coords_ll]
            corner_coords_tgt_prj_np = np.array(corner_coords_tgt_prj)
            x_coords, y_coords = corner_coords_tgt_prj_np[:, 0], corner_coords_tgt_prj_np[:, 1]
            tgt_extent = [np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)]

        return tgt_extent

    def compute_areadefinition_sensor2map(self, data, tgt_prj, tgt_extent=None, tgt_res=None):
        # type: (np.ndarray, Union[int, str], Tuple[float, float, float, float], Tuple[float, float]) -> AreaDefinition
        """Compute the area_definition to resample a sensor geometry array to map geometry.

        :param data:        numpy array to be warped to sensor or map geometry
        :param tgt_prj:     target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:  extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
                            (automatically computed from the corner positions of the coordinate arrays)
        :param tgt_res:     target X/Y resolution (e.g., (30, 30))
        :return:
        """
        tgt_epsg = WKT2EPSG(proj4_to_WKT(get_proj4info(proj=tgt_prj)))
        tgt_extent = tgt_extent or self._get_target_extent(tgt_epsg)

        def raiseErr_if_empty(gdal_ds):
            if not gdal_ds:
                raise Exception(gdal.GetLastErrorMsg())
            return gdal_ds

        with TemporaryDirectory() as td:
            path_xycoords = os.path.join(td, 'xy_coords.bsq')
            path_xycoords_vrt = os.path.join(td, 'xy_coords.vrt')
            path_data = os.path.join(td, 'data.bsq')
            path_datavrt = os.path.join(td, 'data.vrt')
            path_data_out = os.path.join(td, 'data_out.bsq')

            # write X/Y coordinate array
            if tgt_epsg == 4326:
                xy_coords = np.dstack([self.swath_definition.lons,
                                       self.swath_definition.lats])
                # xy_coords = np.dstack([self.swath_definition.lons[::10, ::10],
                #                        self.swath_definition.lats[::10, ::10]])
            else:
                xy_coords = np.dstack(list(transform_coordArray(EPSG2WKT(4326), EPSG2WKT(tgt_epsg),
                                                                self.swath_definition.lons,
                                                                self.swath_definition.lats)))
            write_numpy_to_image(xy_coords, path_xycoords, 'ENVI')

            # create VRT for X/Y coordinate array
            ds_xy_coords = gdal.Open(path_xycoords)
            drv_vrt = gdal.GetDriverByName("VRT")
            vrt = raiseErr_if_empty(drv_vrt.CreateCopy(path_xycoords_vrt, ds_xy_coords))
            del ds_xy_coords, vrt

            # create VRT for one data band
            mask_band = np.ones((data.shape[:2]), np.int32)
            write_numpy_to_image(mask_band, path_data, 'ENVI')
            ds_data = gdal.Open(path_data)
            vrt = raiseErr_if_empty(drv_vrt.CreateCopy(path_datavrt, ds_data))
            vrt.SetMetadata({"X_DATASET": path_xycoords_vrt,
                             "Y_DATASET": path_xycoords_vrt,
                             "X_BAND": "1",
                             "Y_BAND": "2",
                             "PIXEL_OFFSET": "0",
                             "LINE_OFFSET": "0",
                             "PIXEL_STEP": "1",
                             "LINE_STEP": "1",
                             "SRS": EPSG2WKT(tgt_epsg),
                             }, "GEOLOCATION")
            vrt.FlushCache()
            del ds_data, vrt

            subcall_with_output("gdalwarp '%s' '%s' "
                                '-geoloc '
                                '-t_srs EPSG:%d '
                                '-srcnodata 0 '
                                '-r near '
                                '-of ENVI '
                                '-dstnodata none '
                                '-et 0 '
                                '-overwrite '
                                '-te %s '
                                '%s' % (path_datavrt, path_data_out, tgt_epsg,
                                        ' '.join([str(i) for i in tgt_extent]),
                                        ' -tr %s %s' % tgt_res if tgt_res else '',),
                                v=True)

            # get output X/Y size
            ds_out = raiseErr_if_empty(gdal.Open(path_data_out))

            x_size = ds_out.RasterXSize
            y_size = ds_out.RasterYSize
            out_gt = ds_out.GetGeoTransform()

            # noinspection PyUnusedLocal
            ds_out = None

        # add 1 px buffer around out_extent to avoid cutting the output image
        x_size += 2
        y_size += 2
        out_gt = list(out_gt)
        out_gt[0] -= out_gt[1]
        out_gt[3] += abs(out_gt[5])
        out_gt = tuple(out_gt)
        xmin, xmax, ymin, ymax = corner_coord_to_minmax(get_corner_coordinates(gt=out_gt, cols=x_size, rows=y_size))
        out_extent = xmin, ymin, xmax, ymax

        # get area_definition
        area_definition = AreaDefinition(area_id='',
                                         description='',
                                         proj_id='',
                                         projection=get_proj4info(proj=tgt_prj),
                                         width=x_size,
                                         height=y_size,
                                         area_extent=list(out_extent),
                                         )

        return area_definition

    def _resample(self, data, source_geo_def, target_geo_def):
        # type: (np.ndarray, Union[AreaDefinition, SwathDefinition], Union[AreaDefinition, SwathDefinition]) -> ...
        """Run the resampling algorithm.

        :param data:            numpy array to be warped to sensor or map geometry
        :param source_geo_def:  source geo definition
        :param target_geo_def:  target geo definition
        :return:
        """
        if self.resamp_alg == 'nearest':
            opts = {k: v for k, v in self.opts.items() if k not in ['sigmas']}
            result = resample_nearest(source_geo_def, data, target_geo_def, **opts)

        elif self.resamp_alg == 'bilinear':
            opts = {k: v for k, v in self.opts.items() if k not in ['sigmas']}
            result = resample_bilinear(data, source_geo_def, target_geo_def, **opts)

        elif self.resamp_alg == 'gauss':
            opts = {k: v for k, v in self.opts.items()}
            result = resample_gauss(source_geo_def, data, target_geo_def, **opts)

        elif self.resamp_alg == 'custom':
            opts = {k: v for k, v in self.opts.items()}
            if 'weight_funcs' not in opts:
                raise ValueError(opts, "Options must contain a 'weight_funcs' item.")
            result = resample_custom(source_geo_def, data, target_geo_def, **opts)

        else:
            raise ValueError(self.resamp_alg)

        return result  # type: np.ndarray

    @staticmethod
    def _get_gt_prj_from_areadefinition(area_definition):
        # type: (AreaDefinition) -> (Tuple[float, float, float, float, float, float], str)
        gt = area_definition.area_extent[0], area_definition.pixel_size_x, 0, \
             area_definition.area_extent[3], 0, -area_definition.pixel_size_y
        prj = proj4_to_WKT(area_definition.proj_str)

        return gt, prj

    def to_map_geometry(self, data, tgt_prj=None, tgt_extent=None, tgt_res=None, area_definition=None):
        # type: (np.ndarray, Union[str, int], Tuple[float, float, float, float], Tuple, AreaDefinition) -> ...
        """Transform the input sensor geometry array into map geometry.

        :param data:            numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        :param area_definition: an instance of pyresample.geometry.AreaDefinition;
                                OVERRIDES tgt_prj, tgt_extent and tgt_res; saves computation time
        """
        if self.lons.ndim > 2 >= data.ndim:
            raise ValueError(data.ndim, "'data' must at least have %d dimensions because of %d longiture array "
                                        "dimensions." % (self.lons.ndim, self.lons.ndim))

        if data.shape[:2] != self.lons.shape[:2]:
            raise ValueError(data.shape, 'Expected a sensor geometry data array with %d rows and %d columns.'
                             % self.lons.shape[:2])

        # get area_definition
        if area_definition:
            self.area_definition = area_definition
        else:
            if not tgt_prj:
                raise ValueError(tgt_prj, 'Target projection must be given if area_definition is not given.')

            self.area_definition = self.compute_areadefinition_sensor2map(
                data, tgt_prj=tgt_prj, tgt_extent=tgt_extent, tgt_res=tgt_res)

        # resample
        data_mapgeo = self._resample(data, self.swath_definition, self.area_definition)
        out_gt, out_prj = self._get_gt_prj_from_areadefinition(self.area_definition)

        # output validation
        if not data_mapgeo.shape[:2] == (self.area_definition.height, self.area_definition.width):
            raise RuntimeError('The computed map geometry output does not have the expected number of rows/columns. '
                               'Expected: %s; output: %s.'
                               % (str((self.area_definition.height, self.area_definition.width)),
                                  str(data_mapgeo.shape[:2])))
        if data.ndim > 2 and data_mapgeo.ndim == 2:
            raise RuntimeError('The computed map geometry output only one band instead of the expected %d bands.'
                               % data.shape[2])

        return data_mapgeo, out_gt, out_prj  # type: Tuple[np.ndarray, tuple, str]

    def to_sensor_geometry(self, data, src_prj, src_extent):
        # type: (np.ndarray, Union[str, int], List[float, float, float, float]) -> np.ndarray
        """Transform the input map geometry array into sensor geometry

        :param data:        numpy array (representing map geometry) to be warped to sensor geometry
        :param src_prj:     projection of the input map geometry array (WKT or 'epsg:1234' or <EPSG_int>)
        :param src_extent:  extent coordinates of input map geometry array (LL_x, LL_y, UR_x, UR_y) in the src_prj
        """
        proj4_args = proj4_to_dict(get_proj4info(proj=src_prj))

        # get area_definition
        self.area_definition = AreaDefinition('', '', '', proj4_args, data.shape[1], data.shape[0],
                                              src_extent)

        # resample
        data_sensorgeo = self._resample(data, self.area_definition, self.swath_definition)

        # output validation
        if not data_sensorgeo.shape == self.lats.shape:
            raise RuntimeError('The computed sensor geometry output does not have the same size like the coordinates '
                               'array. Coordinates array: %s; output array: %s.'
                               % (self.lats.shape, data_sensorgeo.shape))

        return data_sensorgeo


_global_shared_lats = None
_global_shared_lons = None
_global_shared_data = None


def _initializer(lats, lons, data):
    """Declare global variables needed for SensorMapGeometryTransformer3D.to_map_geometry and to_sensor_geometry.

    :param lats:
    :param lons:
    :param data:
    """
    global _global_shared_lats, _global_shared_lons, _global_shared_data
    _global_shared_lats = lats
    _global_shared_lons = lons
    _global_shared_data = data


class SensorMapGeometryTransformer3D(object):
    def __init__(self, lons, lats, resamp_alg='nearest', radius_of_influence=30, mp_alg='auto', **opts):
        # type: (np.ndarray, np.ndarray, str, int, str, Any) -> None
        """Get an instance of SensorMapGeometryTransformer.

        :param lons:    3D longitude array corresponding to the 3D sensor geometry array
        :param lats:    3D latitude array corresponding to the 3D sensor geometry array

        :Keyword Arguments:  (further documentation here: https://pyresample.readthedocs.io/en/latest/swath.html)
            - resamp_alg:           resampling algorithm ('nearest', 'bilinear', 'gauss', 'custom')
            - radius_of_influence:  <float> Cut off distance in meters (default: 30)
                                    NOTE: keyword is named 'radius' in case of bilinear resampling
            - mp_alg                multiprocessing algorithm
                                    'bands': parallelize over bands using multiprocessing lib
                                    'tiles': parallelize over tiles using OpenMP
                                    'auto': automatically choose the algorithm
            - sigmas:               <list of floats or float> [ONLY 'gauss'] List of sigmas to use for the gauss
                                    weighting of each channel 1 to k, w_k = exp(-dist^2/sigma_k^2). If only one channel
                                    is resampled sigmas is a single float value.
            - neighbours:           <int> [ONLY 'bilinear', 'gauss'] Number of neighbours to consider for each grid
                                    point when searching the closest corner points
            - epsilon:              <float> Allowed uncertainty in meters. Increasing uncertainty reduces execution time
            - weight_funcs:         <list of function objects or function object> [ONLY 'custom'] List of weight
                                    functions f(dist) to use for the weighting of each channel 1 to k. If only one
                                    channel is resampled weight_funcs is a single function object.
            - fill_value:           <int or None> Set undetermined pixels to this value.
                                    If fill_value is None a masked array is returned with undetermined pixels masked
            - reduce_data:          <bool> Perform initial coarse reduction of source dataset in order to reduce
                                    execution time
            - nprocs:               <int>, Number of processor cores to be used
            - segments:             <int or None> Number of segments to use when resampling.
                                    If set to None an estimate will be calculated
            - with_uncert:          <bool> [ONLY 'gauss' and 'custom'] Calculate uncertainty estimates
                                    NOTE: resampling function has 3 return values instead of 1: result, stddev, count
        """
        # validation
        if lons.ndim != 3:
            raise ValueError('Expected a 3D longitude array. Received a %dD array.' % lons.ndim)
        if lats.ndim != 3:
            raise ValueError('Expected a 3D latitude array. Received a %dD array.' % lats.ndim)
        if lons.shape != lats.shape:
            raise ValueError((lons.shape, lats.shape), "'lons' and 'lats' are expected to have the same shape.")

        self.lats = lats
        self.lons = lons
        self.resamp_alg = resamp_alg
        self.radius_of_influence = radius_of_influence
        self.opts = opts

        # define number of CPUs to use (but avoid sub-multiprocessing)
        #   -> parallelize either over bands or over image tiles
        #      bands: multiprocessing uses multiprocessing.Pool, implemented in to_map_geometry / to_sensor_geometry
        #      tiles: multiprocessing uses OpenMP implemented in pykdtree which is used by pyresample
        self.opts['nprocs'] = opts.get('nprocs', multiprocessing.cpu_count())
        self.mp_alg = ('bands' if self.lons.shape[2] >= opts['nprocs'] else 'tiles') if mp_alg == 'auto' else mp_alg

        # override self.mp_alg if SensorMapGeometryTransformer3D is called by nosetest or unittest
        is_called_by_nose_cmd = 'nosetest' in sys.argv[0]
        if self.opts['nprocs'] > 1 and self.mp_alg == 'bands' and is_called_by_nose_cmd:
            warnings.warn("mp_alg='bands' causes deadlocks if SensorMapGeometryTransformer3D is called within a "
                          "nosetest console call. Using mp_alg='tiles'.")
            self.mp_alg = 'tiles'

    @staticmethod
    def _to_map_geometry_2D(kwargs_dict):
        # type: (dict) -> Tuple[np.ndarray, tuple, str, int]
        assert [var is not None for var in (_global_shared_lons, _global_shared_lats, _global_shared_data)]

        SMGT2D = SensorMapGeometryTransformer(lons=_global_shared_lons[:, :, kwargs_dict['band_idx']],
                                              lats=_global_shared_lats[:, :, kwargs_dict['band_idx']],
                                              resamp_alg=kwargs_dict['resamp_alg'],
                                              radius_of_influence=kwargs_dict['radius_of_influence'],
                                              **kwargs_dict['init_opts'])
        data_mapgeo, out_gt, out_prj = SMGT2D.to_map_geometry(data=_global_shared_data[:, :, kwargs_dict['band_idx']],
                                                              tgt_prj=kwargs_dict['tgt_prj'],
                                                              tgt_extent=kwargs_dict['tgt_extent'],
                                                              tgt_res=kwargs_dict['tgt_res'])

        return data_mapgeo, out_gt, out_prj, kwargs_dict['band_idx']

    def _get_common_target_extent(self, tgt_epsg):
        corner_coords_ll = [[self.lons[0, 0, :].min(), self.lats[0, 0, :].max()],  # common UL_xy
                            [self.lons[0, -1, :].max(), self.lats[0, -1, :].max()],  # common UR_xy
                            [self.lons[-1, 0, :].min(), self.lats[-1, 0, :].min()],  # common LL_xy
                            [self.lons[-1, -1, :].max(), self.lats[-1, -1, :].min()],  # common LR_xy
                            ]
        corner_coords_tgt_prj = [transform_any_prj(EPSG2WKT(4326), EPSG2WKT(tgt_epsg), x, y)
                                 for x, y in corner_coords_ll]
        corner_coords_tgt_prj_np = np.array(corner_coords_tgt_prj)
        x_coords, y_coords = corner_coords_tgt_prj_np[:, 0], corner_coords_tgt_prj_np[:, 1]
        tgt_extent = [np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)]

        return tgt_extent

    def to_map_geometry(self, data, tgt_prj, tgt_extent=None, tgt_res=None):
        # type: (np.ndarray, Union[str, int], Tuple[float, float, float, float], Tuple) -> ...
        """Transform the input sensor geometry array into map geometry.

        :param data:            3D numpy array (representing sensor geometry) to be warped to map geometry
        :param tgt_prj:         target projection (WKT or 'epsg:1234' or <EPSG_int>)
        :param tgt_extent:      extent coordinates of output map geometry array (LL_x, LL_y, UR_x, UR_y) in the tgt_prj
        :param tgt_res:         target X/Y resolution (e.g., (30, 30))
        """
        if data.ndim != 3:
            raise ValueError(data.ndim, "'data' must have 3 dimensions.")

        if data.shape != self.lons.shape:
            raise ValueError(data.shape, 'Expected a sensor geometry data array with %d rows, %d columns and %d bands.'
                             % self.lons.shape)

        # get common target extent
        tgt_epsg = WKT2EPSG(proj4_to_WKT(get_proj4info(proj=tgt_prj)))
        tgt_extent = tgt_extent or self._get_common_target_extent(tgt_epsg)

        init_opts = self.opts.copy()
        if self.mp_alg == 'bands':
            del init_opts['nprocs']  # avoid sub-multiprocessing

        args = [dict(
            resamp_alg=self.resamp_alg,
            radius_of_influence=self.radius_of_influence,
            init_opts=init_opts,
            tgt_prj=tgt_prj,
            tgt_extent=tgt_extent,
            tgt_res=tgt_res,
            band_idx=band
        ) for band in range(data.shape[2])]

        if self.opts['nprocs'] > 1 and self.mp_alg == 'bands':
            with multiprocessing.Pool(self.opts['nprocs'],
                                      initializer=_initializer,
                                      initargs=(self.lats, self.lons, data)) as pool:
                result = pool.map(self._to_map_geometry_2D, args)
        else:
            _initializer(self.lats, self.lons, data)
            result = [self._to_map_geometry_2D(argsdict) for argsdict in args]

        band_inds = list(np.array(result)[:, -1])
        data_mapgeo = np.dstack([result[band_inds.index(i)][0] for i in range(data.shape[2])])
        out_gt = result[0][1]
        out_prj = result[0][2]

        return data_mapgeo, out_gt, out_prj  # type: Tuple[np.ndarray, tuple, str]

    @staticmethod
    def _to_sensor_geometry_2D(kwargs_dict):
        # type: (dict) -> (np.ndarray, int)
        assert [var is not None for var in (_global_shared_lons, _global_shared_lats, _global_shared_data)]

        SMGT2D = SensorMapGeometryTransformer(lons=_global_shared_lons[:, :, kwargs_dict['band_idx']],
                                              lats=_global_shared_lats[:, :, kwargs_dict['band_idx']],
                                              resamp_alg=kwargs_dict['resamp_alg'],
                                              radius_of_influence=kwargs_dict['radius_of_influence'],
                                              **kwargs_dict['init_opts'])
        data_sensorgeo = SMGT2D.to_sensor_geometry(data=_global_shared_data[:, :, kwargs_dict['band_idx']],
                                                   src_prj=kwargs_dict['src_prj'],
                                                   src_extent=kwargs_dict['src_extent'])

        return data_sensorgeo, kwargs_dict['band_idx']

    def to_sensor_geometry(self, data, src_prj, src_extent):
        # type: (np.ndarray, Union[str, int], List[float, float, float, float]) -> np.ndarray
        """Transform the input map geometry array into sensor geometry

        :param data:        3D numpy array (representing map geometry) to be warped to sensor geometry
        :param src_prj:     projection of the input map geometry array (WKT or 'epsg:1234' or <EPSG_int>)
        :param src_extent:  extent coordinates of input map geometry array (LL_x, LL_y, UR_x, UR_y) in the src_prj
        """
        if data.ndim != 3:
            raise ValueError(data.ndim, "'data' must have 3 dimensions.")

        init_opts = self.opts.copy()
        if self.mp_alg == 'bands':
            del init_opts['nprocs']  # avoid sub-multiprocessing

        args = [dict(
            resamp_alg=self.resamp_alg,
            radius_of_influence=self.radius_of_influence,
            init_opts=init_opts,
            src_prj=src_prj,
            src_extent=src_extent,
            band_idx=band
        ) for band in range(data.shape[2])]

        if self.opts['nprocs'] > 1 and self.mp_alg == 'bands':
            with multiprocessing.Pool(self.opts['nprocs'],
                                      initializer=_initializer,
                                      initargs=(self.lats, self.lons, data)) as pool:
                result = pool.map(self._to_sensor_geometry_2D, args)
        else:
            _initializer(self.lats, self.lons, data)
            result = [self._to_sensor_geometry_2D(argsdict) for argsdict in args]

        band_inds = list(np.array(result)[:, -1])
        data_sensorgeo = np.dstack([result[band_inds.index(i)][0] for i in range(data.shape[2])])

        return data_sensorgeo
