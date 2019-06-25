import osgeo.gdalnumeric as gdalnumeric
import osgeo.gdal_array as gdal_array
import osgeo.gdal as gdal
from typing import Union
import osgeo.osr as osr
import osgeo.gdalconst
import numpy as np
import tempfile
import errno
import os

# importing system-specific modules
try:
    import crs as osge_c
except ModuleNotFoundError:
    import osgeo_easy.crs as osge_c

DEFAULT_NODATA = -999

__FILEEXT_DRIVER = {
    "tif": "GTiff",
    "tiff": "GTiff",
    "geotiff": "GTiff",
    "bil": "EHdr",
    "nc": "netCDF"
}


def calc_sum(rasters_ref:list, output_file: str=None, no_data: int=DEFAULT_NODATA) -> gdal.Dataset:
    """

    :param rasters_ref:
    :param output_file:
    :param no_data:
    :return:
    """

    if len(rasters_ref) == 0:
        raise TypeError("Empty list of raster references.")

    rasters_ds = [get_dataset(r) for r in rasters_ref]

    # reference dimensions
    base_array = rasters_ds[0].ReadAsArray()
    base_ds, base_matrix = rasters_ds[0], np.full(base_array.shape, no_data, dtype=np.float32)
    del base_array

    # function that will be applied
    def sum_cell(val_a, val_b):
        if val_a == no_data:
            return val_b
        elif val_b == no_data:
            return val_a
        else:
            return val_a + val_b

    # Set values
    # TODO: make it more efficient
    for raster_ds in rasters_ds:
        raster_mtx = raster_ds.ReadAsArray()
        if (raster_mtx.shape[0] != base_matrix.shape[0]) or (raster_mtx.shape[1] != base_matrix.shape[1]):
            print("Rasters have different shapes: {0} x {1}".format(base_matrix.shape, raster_mtx))
            break

        for i in range(base_matrix.shape[0]):
            for j in range(base_matrix.shape[1]):
                base_matrix[i][j] = sum_cell(raster_mtx[i][j], base_matrix[i][j])

    # transform array into a dataset
    ret_ds = gdal_array.OpenArray(base_matrix)
    gdalnumeric.CopyDatasetInfo(base_ds, ret_ds)
    ret_ds.GetRasterBand(1).SetNoDataValue(no_data)
    ret_ds = fill_crs_if_needed(ret_ds)

    # save file if needed
    if output_file is not None:
        write(ret_ds, output_file)

    return ret_ds


def mask(raster_ref, ignore_values: Union[list, None] = None, output_file: str=None) -> gdal.Dataset:
    """

    :param raster_ref:
    :param ignore_values:
    :param output_file:
    :return:
    """

    raster_ds = get_dataset(raster_ref)

    # consolidate list of values to be turned 'zero' into 'ignored_values' variable
    ignored_values = []
    own_nodata = raster_ds.GetRasterBand(1).GetNoDataValue()
    if ((len(ignore_values) <= 0) or (ignore_values is None)) and (own_nodata is None):
        raise TypeError("At least one value to be ignored must be provided when input raster does not have NO DATA.")
    if (len(ignore_values) <= 0) or (ignore_values is None):
        ignored_values.append(own_nodata)
    elif own_nodata is None:
        ignored_values = ignore_values
    else:
        ignored_values = ignore_values + [own_nodata, ]
    del own_nodata

    # function to be applied into each value in raster
    def mask_val(v):
        return 1 if v not in ignored_values else 0

    # apply masking function
    mask_val_vec = np.vectorize(mask_val)
    data_array = raster_ds.ReadAsArray()
    mask_array = mask_val_vec(data_array)
    del mask_val, mask_val_vec, data_array

    # transform array into a dataset
    ret_ds = gdal_array.OpenArray(mask_array)
    gdalnumeric.CopyDatasetInfo(raster_ds, ret_ds)
    ret_ds = fill_crs_if_needed(ret_ds)

    # save file if needed
    if output_file is not None:
        write(ret_ds, output_file)

    return ret_ds


def calc_max(rasters_ref:list, output_file: str=None, no_data: int=DEFAULT_NODATA) -> gdal.Dataset:
    """

    :param rasters_ref:
    :param output_file:
    :param no_data:
    :return:
    """

    if len(rasters_ref) == 0:
        raise TypeError("Empty list of raster references.")

    rasters_ds = [get_dataset(r) for r in rasters_ref]

    # reference dimensions
    base_array = rasters_ds[0].ReadAsArray()
    base_ds, base_matrix = rasters_ds[0], np.full(base_array.shape, no_data, dtype=np.float32)
    del base_array

    # function that will be applied
    def max_cell(val_a, val_b):
        if val_a == no_data:
            return val_b
        elif val_b == no_data:
            return val_a
        else:
            return max(val_a, val_b)

    # Set values
    # TODO: make it more efficient
    for raster_ds in rasters_ds:
        raster_mtx = raster_ds.ReadAsArray()
        if (raster_mtx.shape[0] != base_matrix.shape[0]) or (raster_mtx.shape[1] != base_matrix.shape[1]):
            print("Rasters have different shapes: {0} x {1}".format(base_matrix.shape, raster_mtx))
            break

        for i in range(base_matrix.shape[0]):
            for j in range(base_matrix.shape[1]):
                base_matrix[i][j] = max_cell(raster_mtx[i][j], base_matrix[i][j])

    # transform array into a dataset
    ret_ds = gdal_array.OpenArray(base_matrix)
    gdalnumeric.CopyDatasetInfo(base_ds, ret_ds)
    ret_ds.GetRasterBand(1).SetNoDataValue(no_data)
    ret_ds = fill_crs_if_needed(ret_ds)

    # save file if needed
    if output_file is not None:
        write(ret_ds, output_file)

    return ret_ds


def calc_count_data_percent(rasters_ref:list, output_file: str=None, no_data: list=(DEFAULT_NODATA,)) -> gdal.Dataset:
    """

    :param rasters_ref:
    :param output_file:
    :param no_data:
    :return:
    """

    if len(rasters_ref) == 0:
        raise TypeError("Empty list of raster references.")

    rasters_ds = [get_dataset(r) for r in rasters_ref]

    # reference dimensions
    base_array = rasters_ds[0].ReadAsArray()
    base_ds, base_matrix = rasters_ds[0], np.full(base_array.shape, 0.0, dtype=np.float32)
    del base_array

    # function that will be applied
    def count_cell(val_a, val_b):
        return val_b if val_a in no_data else val_b + 1

    # Set values
    # TODO: make it more efficient
    for raster_ds in rasters_ds:
        raster_mtx = raster_ds.ReadAsArray()
        if (raster_mtx.shape[0] != base_matrix.shape[0]) or (raster_mtx.shape[1] != base_matrix.shape[1]):
            print("Rasters have different shapes: {0} x {1}".format(base_matrix.shape, raster_mtx))
            break

        for i in range(base_matrix.shape[0]):
            for j in range(base_matrix.shape[1]):
                base_matrix[i][j] = count_cell(raster_mtx[i][j], base_matrix[i][j])

    # make accumulated value a percent
    base_matrix /= len(rasters_ref)

    # transform array into a dataset
    ret_ds = gdal_array.OpenArray(base_matrix)
    gdalnumeric.CopyDatasetInfo(base_ds, ret_ds)
    # ret_ds.GetRasterBand(1).SetNoDataValue(no_data)
    ret_ds = fill_crs_if_needed(ret_ds)

    # save file if needed
    if output_file is not None:
        write(ret_ds, output_file)

    return ret_ds


def calc_mean(rasters_ref: list, replace_nodata: Union[bool, float, int]=False, output_file: str=None) -> gdal.Dataset:
    """

    :param rasters_ref:
    :param replace_nodata: If boolean False: NoData=NoData. If boolean True: NoData=same. If float/int val: NoData=val
    :param output_file:
    :return:
    """

    if len(rasters_ref) == 0:
        raise TypeError("Empty list of raster references.")

    # read data and build cube
    rasters_ds = [get_dataset(r) for r in rasters_ref]
    base_ds = rasters_ds[0]
    no_data = base_ds.GetRasterBand(1).GetNoDataValue()
    cube = np.dstack([raster_ds.ReadAsArray() for raster_ds in rasters_ds])
    del rasters_ds

    # function to be applied
    def mean_collumn(values: np.core.multiarray):
        if isinstance(replace_nodata, bool) and replace_nodata:
            return no_data if no_data in values else np.mean(values)
        elif isinstance(replace_nodata, bool) and not replace_nodata:
            valid_values = [v for v in values if v != no_data]
            return no_data if len(valid_values) == 0 else np.mean(valid_values)
        else:
            return np.mean(np.where(values == no_data, replace_nodata, values))

    base_matrix = np.apply_along_axis(mean_collumn, 2, cube)

    # transform array into a dataset
    ret_ds = gdal_array.OpenArray(base_matrix)
    gdalnumeric.CopyDatasetInfo(base_ds, ret_ds)
    if no_data is not None:
        ret_ds.GetRasterBand(1).SetNoDataValue(no_data)
    ret_ds = fill_crs_if_needed(ret_ds)

    # save file if needed
    if output_file is not None:
        write(ret_ds, output_file)

    return ret_ds


def get_dataset(raster_ref) -> gdal.Dataset:
    """
    Always return a gdal.Dataset
    :param raster_ref: String (raster file path) or gdal.Dataset
    :return:
    """
    if isinstance(raster_ref, str):
        return read(raster_ref)
    elif isinstance(raster_ref, gdal.Dataset):
        return raster_ref
    else:
        raise TypeError


def get_epsg(ref) -> int:
    """

    :param ref: File path or ogr.DataSource or osr.SpatialReference
    :return:
    """
    if isinstance(ref, str) or isinstance(ref, gdal.Dataset):
        return int(get_spatial_reference(ref).GetAttrValue("AUTHORITY", 1))
    elif isinstance(ref, osr.SpatialReference):
        return ref.GetAttrValue("AUTHORITY", 1)
    elif isinstance(ref, int):
        return ref
    else:
        raise TypeError


def fill_crs_if_needed(raster_ref, output_crs: int=osge_c.DEFAULT_EPSG) -> gdal.Dataset:
    """

    :param raster_ref:
    :param output_crs:
    :return:
    """

    raster_ds = get_dataset(raster_ref)
    inp_raster_proj = raster_ds.GetProjection()

    # if already set a crs, does nothing
    if (inp_raster_proj is not None) and (inp_raster_proj.strip() != ""):
        return raster_ds
    else:
        del inp_raster_proj

    # get spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(output_crs)
    raster_ds.SetProjection(srs.ExportToWkt())

    return raster_ds


def get_spatial_reference(raster_ref) -> osr.SpatialReference:
    """

    :param raster_ref:
    :return:
    """

    raster_ds = get_dataset(raster_ref)
    raster_proj = raster_ds.GetProjection()
    raster_sr = osr.SpatialReference(wkt=raster_proj)

    return raster_sr


def read(file_path: str) -> gdal.Dataset:
    """
    Just overloads osgeo.ogr.Open following PEP-8 standards
    :param file_path:
    :return:
    """

    ret = gdal.Open(file_path)
    if ret is None:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
    return ret


def reproject(raster_ref, output_crs, output_file: str=None) -> gdal.Dataset:
    """
    Gets a new Dataset with the same information, with the same spatial resolution, of the input raster, but in a different coord. ref. system
    :param raster_ref:
    :param output_crs:
    :param output_file:
    :return: New, reprojected gdal.Dataset
    """

    rst_ds = get_dataset(raster_ref)
    rst_ds = fill_crs_if_needed(rst_ds)
    inp_epsg, out_epsg = get_epsg(rst_ds), get_epsg(output_crs)

    # check if reprojection is unnecessary
    if inp_epsg == out_epsg:
        if output_file is not None:
            # TODO
            raise NotImplemented("Feature for saving a reprojected raster.")
        return rst_ds

    raise NotImplementedError("Effective reprojection of raster.")


def resample(source_raster_ref, template_raster_ref=None, output_file: str=None,
             output_gdtype: int=osgeo.gdalconst.GDT_Float32,
             gdal_resample_algorithm: int=osgeo.gdalconst.GRA_Bilinear) -> gdal.Dataset:
    """
    Gets a new Dataset with the same information as in a source raster but in the projection as spatial resolution as a template raster file
    :param source_raster_ref: Raster used as data source
    :param template_raster_ref: Raster used as template
    :param output_file: File path to be written
    :param output_gdtype: Expected osgeo.gdalconst.GDT_Float32, osgeo.gdalconst.GDT_..., etc
    :param gdal_resample_algorithm: Expected osgeo.gdalconst.GRA_Average, osgeo.gdalconst.GRA_Bilinear, etc.
    :return: Resampled Dataset
    """

    # get working datasets
    src_rst_ds = get_dataset(source_raster_ref)
    if template_raster_ref is not None:
        tpl_rst_ds = get_dataset(template_raster_ref)
    else:
        raise NotImplementedError("Effective reprojection of raster.")

    # get source metadata
    src_proj, src_geot = tpl_rst_ds.GetProjection(), tpl_rst_ds.GetGeoTransform()

    # get template metadata
    tpl_proj, tpl_geot = tpl_rst_ds.GetProjection(), tpl_rst_ds.GetGeoTransform()
    wide, high = tpl_rst_ds.RasterXSize, tpl_rst_ds.RasterYSize

    # build output
    _, tmp_filepath = tempfile.mkstemp('.tif')
    ret_ds = gdal.GetDriverByName('GTiff').Create(tmp_filepath, wide, high, 1, output_gdtype)
    ret_ds.SetGeoTransform(tpl_geot)
    ret_ds.SetProjection(tpl_proj)

    # do the work
    gdal.ReprojectImage(src_rst_ds, ret_ds, src_proj, tpl_proj, gdal_resample_algorithm)

    # save file if needed
    if output_file is not None:
        write(ret_ds, output_file)

    return ret_ds


def write(raster_ds: gdal.Dataset, file_path: str) -> None:
    """
    Write dataset into a raster file. Abstract the process of getting a GDAL driver.
    """
    driver = __get_driver(file_path)
    driver.CreateCopy(file_path, raster_ds)
    return None


def __get_driver(file_path: str) -> gdal.Driver:
    """

    :param file_path:
    :return:
    """

    splitted = os.path.splitext(file_path)
    if len(splitted) <= 1:
        raise TypeError("Unable to save file without extension (%s)." % file_path)

    file_ext = splitted[-1][1:].lower()
    if file_ext not in __FILEEXT_DRIVER.keys():
        raise TypeError("Unable to finda a driver for file extension '%s'." % file_ext)

    return gdal.GetDriverByName(__FILEEXT_DRIVER[file_ext])
