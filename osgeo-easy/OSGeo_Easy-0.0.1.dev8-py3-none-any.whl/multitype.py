import osgeo.gdalnumeric as gdalnumeric
import osgeo.gdal_array as gdal_array
from PIL import Image, ImageDraw
import osgeo.gdal as gdal
import numpy as np

# importing system-specific modules
try:
    import crs
except ModuleNotFoundError:
    import osgeo_easy.crs as osge_c
try:
    import raster as osge_r
except ModuleNotFoundError:
    import osgeo_easy.raster as osge_r
try:
    import vector as osge_v
except ModuleNotFoundError:
    import osgeo_easy.vector as osge_v


def clip_raster_by_vector_extent(raster_ref, vector_ref, output_file: str=None, output_crs: int=osge_c.DEFAULT_EPSG,
                                 no_data: int=osge_r.DEFAULT_NODATA) -> gdal.Dataset:
    """

    :param raster_ref:
    :param vector_ref:
    :param output_file:
    :param output_crs:
    :param no_data:
    :return:
    """

    inp_raster_ds, inp_vector_ds = osge_r.get_dataset(raster_ref), osge_v.get_datasource(vector_ref)

    # ensure both are in the same output crs
    raster_ds = osge_r.reproject(inp_raster_ds, output_crs)
    vector_ds = osge_v.reproject(inp_vector_ds, output_crs)
    del inp_raster_ds, inp_vector_ds

    # ensure vector has just one layer
    # TODO - make it more flexible
    if vector_ds.GetLayerCount() != 1:
        raise NotImplementedError("Clip only supports a vector object with one layer. "
                                  "Got %d." % vector_ds.GetLayerCount())
    vector_layer = vector_ds.GetLayer()

    # ensure layer has only one polygon
    if vector_layer.GetFeatureCount() != 1:
        raise NotImplementedError("Clip only supports a vector object with one polygon. "
                                  "Got %d." % vector_ds.GetLayerCount())

    # ensure type is polygon
    # TODO

    # get objects
    raster_geotrans = raster_ds.GetGeoTransform()
    vector_feat = vector_layer.GetNextFeature()
    vector_georef = vector_feat.GetGeometryRef()

    # Convert the vector extent to image pixel coordinates
    min_x, max_x, min_y, max_y = vector_georef.GetEnvelope()
    ulX, ulY = __world_to_pixel(raster_geotrans, min_x, max_y)
    lrX, lrY = __world_to_pixel(raster_geotrans, max_x, min_y)
    if None in (ulX, ulY):
        raise IndexError("Unable to define Upper-Left pixels.")
    elif None in (lrX, lrY):
        raise IndexError("Unable to define Lower-Right pixels.")

    # Calculate the pixel size of the new image
    px_w, px_h = int(lrX - ulX), int(lrY - ulY)

    # get subset of raster file into an array
    src_array = gdalnumeric.DatasetReadAsArray(raster_ds)
    try:
        pre_clip = src_array[:, ulY:lrY, ulX:lrX]
    except IndexError:
        pre_clip = src_array[ulY:lrY, ulX:lrX]
    del src_array

    # create a new geomatrix for the image
    geoTrans = list(raster_geotrans)
    geoTrans[0], geoTrans[3] = min_x, max_y
    del min_x, max_y, raster_geotrans

    # Map points to pixels for drawing the boundary on a blank 8-bit,
    # black and white, mask image.
    pts = vector_georef.GetGeometryRef(0)
    points = [(pts.GetX(p), pts.GetY(p)) for p in range(pts.GetPointCount())]
    pixels = [__world_to_pixel(geoTrans, p[0], p[1]) for p in points]
    pixels = [p for p in pixels if None not in p]  # remove failed translations
    del pts, points, geoTrans

    # clip the image using the mask
    rasterPoly = Image.new("L", (px_w, px_h), 1)  # opens a gray-scale ('L') all-white (1) image
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = __image_to_array(rasterPoly)  # 1: outside mask, 0: inside mask
    clip = gdalnumeric.choose(mask, (pre_clip, -999.0))  # effective clipping
    clip = clip.astype(gdalnumeric.float32)
    del pre_clip, mask, rasterize, rasterPoly

    # wrap clipped array into a dataset
    dataset = __open_array(clip, prototype_ds=raster_ds, xoff=ulX, yoff=ulY)
    dataset.GetRasterBand(1).SetNoDataValue(-999.0)

    # TODO - instead of 'filling if needed, ENFORCE the projection set'
    dataset = osge_r.fill_crs_if_needed(dataset, output_crs)
    # dataset.SetProjection(out_proj.ExportToWkt())
    del clip

    # save file if needed
    if output_file is not None:
        osge_r.write(dataset, output_file)

    return dataset


def __image_to_array(i: Image.Image) -> np.ndarray:
    """
    Converts a Python Imaging Library array to a gdalnumeric image.
    """
    a = gdalnumeric.fromstring(i.tobytes(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a


def __open_array(array: np.ndarray, prototype_ds = None, xoff=0, yoff=0) -> gdal.Dataset:
    """
    This is basically an overloaded version of the gdal_array.OpenArray
    passing in xoff, yoff explicitly so we can pass these params off to
    CopyDatasetInfo
    """

    ds = gdal_array.OpenArray(array)

    if (ds is not None) and (prototype_ds is not None):
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal.Open(prototype_ds)
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff )
    else:
        print("d")
    return ds


def __world_to_pixel(geo_matrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """

    try:
        ulX, ulY, xDist = geo_matrix[0], geo_matrix[3], geo_matrix[1]
        pixel, line = int((x - ulX) / xDist), int((ulY - y) / xDist)
        return pixel, line
    except ZeroDivisionError:
        return None, None
