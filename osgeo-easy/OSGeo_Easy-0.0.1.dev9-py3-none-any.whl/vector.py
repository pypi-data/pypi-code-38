import osgeo.ogr as ogr
import osgeo.osr as osr
import tempfile
import errno
import copy
import os

# importing system-specific modules
try:
    import crs as osge_c
except ModuleNotFoundError:
    import osgeo_easy.crs as osge_c

DEFAULT_FILE_DRIVER = ogr.GetDriverByName("ESRI Shapefile")
DEFAULT_FILE_EXTENSION = '.shp'


def get_datasource(vector_ref) -> ogr.DataSource:
    """
    Always return a ogr.DataSource
    :param vector_ref: String (raster file path) or gdal.Dataset
    :return:
    """
    if isinstance(vector_ref, str):
        return read(vector_ref)
    elif isinstance(vector_ref, ogr.DataSource):
        return vector_ref
    else:
        raise TypeError


def get_epsg(ref) -> int:
    """

    :param ref: File path or ogr.DataSource or osr.SpatialReference
    :return:
    """
    if isinstance(ref, str) or isinstance(ref, ogr.DataSource):
        sr = get_spatial_reference(ref)

        # try to get from the root
        attr = sr.GetAttrValue("AUTHORITY", 1)
        if attr is not None:
            return int(attr)

        # try to enforce projection
        sr.AutoIdentifyEPSG()
        attr = sr.GetAttrValue("AUTHORITY", 1)
        if attr is not None:
            return int(attr)

        # try to get from projection
        attr = sr.GetAuthorityCode("PROJCS")
        if attr is not None:
            return int(attr)

        # try to get from coordinate system
        attr = sr.GetAuthorityCode("GEOGCS")
        if attr is not None:
            return int(attr)

        # ok... give it up
        raise TypeError("Unable to identify EPSG code from vector file.")

    elif isinstance(ref, osr.SpatialReference):
        return ref.GetAttrValue("AUTHORITY", 1)
    elif isinstance(ref, int):
        return ref
    else:
        raise TypeError


def get_spatial_reference(ref) -> osr.SpatialReference:
    """

    :param ref:
    :return:
    """
    if isinstance(ref, int):
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(ref)
        return srs
    if isinstance(ref, str) or isinstance(ref, ogr.DataSource):
        vector_ds = get_datasource(ref)
        inp_vector_layer = vector_ds.GetLayer()
        return inp_vector_layer.GetSpatialRef()
    else:
        raise TypeError


def read(file_path: str) -> ogr.DataSource:
    """
    Just overloads osgeo.ogr.Open following PEP-8 standards
    :param file_path:
    :return:
    """

    ret = ogr.Open(file_path)
    if ret is None:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
    return ret


def reproject(vector_ref, output_crs, output_file: str=None) -> ogr.DataSource:
    """

    :param vector_ref:
    :param output_crs:
    :param output_file:
    :return:
    """
    vec_ds = get_datasource(vector_ref)
    inp_epsg, out_epsg = get_epsg(vec_ds), get_epsg(output_crs)

    # check if reprojection is unnecessary
    if inp_epsg == out_epsg:
        if output_file is not None:
            # TODO
            raise NotImplemented
        return vec_ds

    coord_trans = osge_c.get_coordinate_transform(inp_epsg, out_epsg)

    # create output datasource
    inp_layer = vec_ds.GetLayer()
    if output_file is None:
        # define a temporary file path (TODO: change it for something less shameful)
        temp = tempfile.NamedTemporaryFile(suffix=DEFAULT_FILE_EXTENSION)
        out_file_path = temp.name
        temp.close()
        del temp
    else:
        out_file_path = output_file
    out_ds = DEFAULT_FILE_DRIVER.CreateDataSource(out_file_path)
    out_layer = out_ds.CreateLayer(inp_layer.GetName(), get_spatial_reference(out_epsg), inp_layer.GetGeomType())

    # for inp_feature in inp_layer.GetNextFeature():
    inp_feature = inp_layer.GetNextFeature()
    while inp_feature is not None:

        # create new feature out of transformed
        geom = inp_feature.GetGeometryRef()
        geom.Transform(coord_trans)
        out_feature = ogr.Feature(inp_layer.GetLayerDefn())
        out_feature.SetGeometry(geom)

        # set up attributes and add feature to layer
        inp_definitions = inp_layer.GetLayerDefn()
        for i in range(0, inp_definitions.GetFieldCount()):
            out_feature.SetField(inp_definitions.GetFieldDefn(i).GetNameRef(), inp_feature.GetField(i))
        out_layer.CreateFeature(out_feature)

        # next step
        inp_feature = inp_layer.GetNextFeature()

    # write to disk if needed
    if output_file is not None:
        out_ds.SyncToDisk()

    return out_ds
