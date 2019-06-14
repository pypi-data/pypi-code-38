# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os

try:
    from osgeo import gdal
except ImportError:
    import gdal

from ..processing.shell import subcall_with_output
from ..io.pathgen import get_tempfile

__author__ = "Daniel Scheffler"


def Warp(destNameOrDestDS, srcDSOrSrcDSTab, options='', format='GTiff',
         outputBounds=None,
         outputBoundsSRS=None,
         xRes=None, yRes=None, targetAlignedPixels=False,
         width=0, height=0,
         srcSRS=None, dstSRS=None,
         srcAlpha=False, dstAlpha=False,
         warpOptions=None, errorThreshold=None,
         warpMemoryLimit=None, creationOptions=None, outputType=gdal.GDT_Unknown,
         workingType=gdal.GDT_Unknown, resampleAlg=None,
         srcNodata=None, dstNodata=None, multithread=False,
         tps=False, rpc=False, geoloc=False, polynomialOrder=None,
         transformerOptions=None, cutlineDSName=None,
         cutlineLayer=None, cutlineWhere=None, cutlineSQL=None, cutlineBlend=None, cropToCutline=False,
         copyMetadata=True, metadataConflictValue=None,
         setColorInterpretation=False,
         callback=None, callback_data=None):
    """ This functions brings functionality of gdal.Warp() that is not available in GDAL versions below 2.1 (?).

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
          callback_data --- user data for callback
    """

    new_options = options
    # new_options += ['-of', format]
    if outputType != gdal.GDT_Unknown:
        new_options += ['-ot', gdal.GetDataTypeName(outputType)]
    if workingType != gdal.GDT_Unknown:
        new_options += ['-wt', gdal.GetDataTypeName(workingType)]
    if outputBounds is not None:
        new_options += ['-te', str(outputBounds[0]), str(outputBounds[1]), str(outputBounds[2]), str(outputBounds[3])]
    if outputBoundsSRS is not None:
        new_options += ['-te_srs', str(outputBoundsSRS)]
    if xRes is not None and yRes is not None:
        new_options += ['-tr', str(xRes), str(yRes)]
    if width or height:
        new_options += ['-ts', str(width), str(height)]
    if srcSRS is not None:
        new_options += ['-s_srs', str(srcSRS)]
    if dstSRS is not None:
        new_options += ['-t_srs', str(dstSRS)]
    if targetAlignedPixels:
        new_options += ['-tap']
    if srcAlpha:
        new_options += ['-srcalpha']
    if dstAlpha:
        new_options += ['-dstalpha']
    if warpOptions is not None:
        for opt in warpOptions:
            new_options += ['-wo', str(opt)]
    if errorThreshold is not None:
        new_options += ['-et', str(errorThreshold)]
    if resampleAlg is not None:
        if resampleAlg == gdal.GRA_NearestNeighbour:
            new_options += ['-r', 'near']
        elif resampleAlg == gdal.GRA_Bilinear:
            new_options += ['-rb']
        elif resampleAlg == gdal.GRA_Cubic:
            new_options += ['-rc']
        elif resampleAlg == gdal.GRA_CubicSpline:
            new_options += ['-rcs']
        elif resampleAlg == gdal.GRA_Lanczos:
            new_options += ['-r', 'lanczos']
        elif resampleAlg == gdal.GRA_Average:
            new_options += ['-r', 'average']
        elif resampleAlg == gdal.GRA_Mode:
            new_options += ['-r', 'mode']
        else:  # gdal.GRA_Gauss is missing
            new_options += ['-r', str(resampleAlg)]
    if warpMemoryLimit is not None:
        new_options += ['-wm', str(warpMemoryLimit)]
    if creationOptions is not None:
        for opt in creationOptions:
            new_options += ['-co', opt]
    if srcNodata is not None:
        new_options += ['-srcnodata', str(srcNodata)]
    if dstNodata is not None:
        new_options += ['-dstnodata', str(dstNodata)]
    if multithread:
        new_options += ['-multi']
    if tps:
        new_options += ['-tps']
    if rpc:
        new_options += ['-rpc']
    if geoloc:
        new_options += ['-geoloc']
    if polynomialOrder is not None:
        new_options += ['-order', str(polynomialOrder)]
    if transformerOptions is not None:
        for opt in transformerOptions:
            new_options += ['-to', opt]
    if cutlineDSName is not None:
        new_options += ['-cutline', str(cutlineDSName)]
    if cutlineLayer is not None:
        new_options += ['-cl', str(cutlineLayer)]
    if cutlineWhere is not None:
        new_options += ['-cwhere', str(cutlineWhere)]
    if cutlineSQL is not None:
        new_options += ['-csql', str(cutlineSQL)]
    if cutlineBlend is not None:
        new_options += ['-cblend', str(cutlineBlend)]
    if cropToCutline:
        new_options += ['-crop_to_cutline']
    if not copyMetadata:
        new_options += ['-nomd']
    if metadataConflictValue:
        new_options += ['-cvmd', str(metadataConflictValue)]
    if setColorInterpretation:
        new_options += ['-setci']

    if isinstance(srcDSOrSrcDSTab, gdal.Dataset):
        drv = gdal.GetDriverByName('ENVI')
        inPath = get_tempfile(prefix='warp_in_', ext='.bsq')
        drv.CreateCopy(inPath, srcDSOrSrcDSTab)
        del srcDSOrSrcDSTab
    elif isinstance(srcDSOrSrcDSTab, str):
        inPath = srcDSOrSrcDSTab
    else:
        raise ValueError

    warpedPath = get_tempfile(prefix='warp_out_', ext='.bsq')
    out, exitcode, err = subcall_with_output('gdalwarp %s %s -of ENVI -overwrite %s'
                                             % (inPath, warpedPath, ' '.join(new_options)))
    if exitcode:
        raise Exception(err)

    ds = gdal.Open(warpedPath)
    if ds is None:
        raise Exception(gdal.GetLastErrorMsg())

    drv = gdal.GetDriverByName('MEM')
    mem_ds = drv.CreateCopy(warpedPath, ds)

    # cleanup
    del ds
    [gdal.Unlink(p) for p in [inPath, os.path.splitext(inPath)[0] + '.hdr']]
    [gdal.Unlink(p) for p in [warpedPath, os.path.splitext(warpedPath)[0] + '.hdr']]

    return mem_ds


def Translate(destNameOrDestDS, srcDSOrSrcDSTab, options='', format='GTiff',
              outputType=gdal.GDT_Unknown, bandList=None, maskBand=None,
              width=0, height=0, widthPct=0.0, heightPct=0.0,
              xRes=0.0, yRes=0.0,
              creationOptions=None, srcWin=None, projWin=None, projWinSRS=None, strict=False,
              unscale=False, scaleParams=None, exponents=None,
              outputBounds=None, metadataOptions=None,
              outputSRS=None, GCPs=None,
              noData=None, rgbExpand=None,
              stats=False, rat=True, resampleAlg=None,
              callback=None, callback_data=None):
    """ This functions brings functionality of gdal.Translate() that is not available in GDAL versions below 2.1 (?).

        Keyword arguments are :
          options --- can be be an array of strings, a string or let empty and filled from other keywords.
          format --- output format ("GTiff", etc...)
          outputType --- output type (gdal.GDT_Byte, etc...)
          bandList --- array of band numbers (index start at 1)
          maskBand --- mask band to generate or not ("none", "auto", "mask", 1, ...)
          width --- width of the output raster in pixel
          height --- height of the output raster in pixel
          widthPct --- width of the output raster in percentage (100 = original width)
          heightPct --- height of the output raster in percentage (100 = original height)
          xRes --- output horizontal resolution
          yRes --- output vertical resolution
          creationOptions --- list of creation options
          srcWin --- subwindow in pixels to extract: [left_x, top_y, width, height]
          projWin --- subwindow in projected coordinates to extract: [ulx, uly, lrx, lry]
          projWinSRS --- SRS in which projWin is expressed
          strict --- strict mode
          unscale --- unscale values with scale and offset metadata
          scaleParams --- list of scale parameters, each of the form
                          [src_min,src_max] or [src_min,src_max,dst_min,dst_max]
          exponents --- list of exponentiation parameters
          outputBounds --- assigned output bounds: [ulx, uly, lrx, lry]
          metadataOptions --- list of metadata options
          outputSRS --- assigned output SRS
          GCPs --- list of GCPs
          noData --- nodata value (or "none" to unset it)
          rgbExpand --- Color palette expansion mode: "gray", "rgb", "rgba"
          stats --- whether to calculate statistics
          rat --- whether to write source RAT
          resampleAlg --- resampling mode
          callback --- callback method
          callback_data --- user data for callback
    """

    new_options = options
    new_options += ['-of', format]
    if outputType != gdal.GDT_Unknown:
        new_options += ['-ot', gdal.GetDataTypeName(outputType)]
    if maskBand is not None:
        new_options += ['-mask', str(maskBand)]
    if bandList is not None:
        for b in bandList:
            new_options += ['-b', str(b)]
    if width != 0 or height != 0:
        new_options += ['-outsize', str(width), str(height)]
    elif widthPct != 0 and heightPct != 0:
        new_options += ['-outsize', str(widthPct) + '%%', str(heightPct) + '%%']
    if creationOptions is not None:
        for opt in creationOptions:
            new_options += ['-co', opt]
    if srcWin is not None:
        new_options += ['-srcwin', str(srcWin[0]), str(srcWin[1]), str(srcWin[2]), str(srcWin[3])]
    if strict:
        new_options += ['-strict']
    if unscale:
        new_options += ['-unscale']
    if scaleParams:
        for scaleParam in scaleParams:
            new_options += ['-scale']
            for v in scaleParam:
                new_options += [str(v)]
    if exponents:
        for exponent in exponents:
            new_options += ['-exponent', str(exponent)]
    if outputBounds is not None:
        new_options += ['-a_ullr', str(outputBounds[0]), str(outputBounds[1]), str(outputBounds[2]),
                        str(outputBounds[3])]
    if metadataOptions is not None:
        for opt in metadataOptions:
            new_options += ['-mo', opt]
    if outputSRS is not None:
        new_options += ['-a_srs', str(outputSRS)]
    if GCPs is not None:
        for gcp in GCPs:
            new_options += ['-gcp', str(gcp.GCPPixel), str(gcp.GCPLine), str(gcp.GCPX), str(gcp.GCPY), str(gcp.GCPZ)]
    if projWin is not None:
        new_options += ['-projwin', str(projWin[0]), str(projWin[1]), str(projWin[2]), str(projWin[3])]
    if projWinSRS is not None:
        new_options += ['-projwin_srs', str(projWinSRS)]
    if noData is not None:
        new_options += ['-a_nodata', str(noData)]
    if rgbExpand is not None:
        new_options += ['-expand', str(rgbExpand)]
    if stats:
        new_options += ['-stats']
    if not rat:
        new_options += ['-norat']
    if resampleAlg is not None:
        if resampleAlg == gdal.GRA_NearestNeighbour:
            new_options += ['-r', 'near']
        elif resampleAlg == gdal.GRA_Bilinear:
            new_options += ['-r', 'bilinear']
        elif resampleAlg == gdal.GRA_Cubic:
            new_options += ['-r', 'cubic']
        elif resampleAlg == gdal.GRA_CubicSpline:
            new_options += ['-r', 'cubicspline']
        elif resampleAlg == gdal.GRA_Lanczos:
            new_options += ['-r', 'lanczos']
        elif resampleAlg == gdal.GRA_Average:
            new_options += ['-r', 'average']
        elif resampleAlg == gdal.GRA_Mode:
            new_options += ['-r', 'mode']
        else:
            new_options += ['-r', str(resampleAlg)]
    if xRes != 0 and yRes != 0:
        new_options += ['-tr', str(xRes), str(yRes)]

    if isinstance(srcDSOrSrcDSTab, gdal.Dataset):
        drv = gdal.GetDriverByName('ENVI')
        inPath = get_tempfile(prefix='translate_in_', ext='.bsq')
        drv.CreateCopy(inPath, srcDSOrSrcDSTab)
        del srcDSOrSrcDSTab
    elif isinstance(srcDSOrSrcDSTab, str):
        inPath = srcDSOrSrcDSTab
    else:
        raise ValueError

    translatedPath = get_tempfile(prefix='translate_out_', ext='.bsq')
    out, exitcode, err = subcall_with_output('gdal_translate %s %s -of ENVI %s'
                                             % (inPath, translatedPath, ' '.join(new_options)))
    if exitcode:
        raise Exception(err)

    ds = gdal.Open(translatedPath)
    if ds is None:
        raise Exception(gdal.GetLastErrorMsg())

    drv = gdal.GetDriverByName('MEM')
    mem_ds = drv.CreateCopy(translatedPath, ds)

    # cleanup
    del ds
    [gdal.Unlink(p) for p in [inPath, os.path.splitext(inPath)[0] + '.hdr']]
    [gdal.Unlink(p) for p in [translatedPath, os.path.splitext(translatedPath)[0] + '.hdr']]

    return mem_ds


def ensure_GDAL_version_compatibility(func2run, funcName2ensure):
    import functools
    try:
        getattr(gdal, funcName2ensure)
    except AttributeError:
        if funcName2ensure in globals():
            setattr(gdal, funcName2ensure, globals()[funcName2ensure])
        else:
            raise AttributeError("'gdal' has no attribute '%s'." % funcName2ensure)

    @functools.wraps(func2run)
    def inner(*args, **kwargs):
        return func2run(*args, **kwargs)

    return inner


def ensure_GDAL_version_compatibility_deco(funcName2ensure):
    try:
        getattr(gdal, funcName2ensure)
        funcIsMissing = False
    except AttributeError:
        funcIsMissing = True
        print('drin1')
        if funcName2ensure in globals():
            print('drin2')
            setattr(gdal, funcName2ensure, globals()[funcName2ensure])
            print('pre', globals()[funcName2ensure])
            gdal.Warp = globals()[funcName2ensure]
            from gdal import Warp
            print('pre2', Warp)
            # print(importlib.import_module('gdal.%s' % funcName2ensure))
        else:
            raise AttributeError("'gdal' has no attribute '%s'." % funcName2ensure)

    def real_decorator(function):
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    if funcIsMissing:
        delattr(gdal, funcName2ensure)

    return real_decorator


def get_gdal_func(funcName):
    try:
        return getattr(gdal, funcName)
    except AttributeError:
        if funcName in globals():
            return globals()[funcName]
        else:
            raise AttributeError("'gdal' has no attribute '%s'." % funcName)
