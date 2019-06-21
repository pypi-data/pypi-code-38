import os
import struct
from math import isnan

import iso8601
import numpy as np
from affine import Affine
from htimeseries import HTimeseries
from osgeo import gdal, ogr, osr

gdal.UseExceptions()

NODATAVALUE = -2.0 ** 127


def idw(point, data_layer, alpha=1):
    data_layer.ResetReading()
    features = [f for f in data_layer if not isnan(f.GetField("value"))]
    distances = np.array([point.Distance(f.GetGeometryRef()) for f in features])
    values = np.array([f.GetField("value") for f in features])
    matches_station_exactly = abs(distances) < 1e-3
    if matches_station_exactly.any():
        invdistances = np.where(matches_station_exactly, 1, 0)
    else:
        invdistances = distances ** (-alpha)
    weights = invdistances / invdistances.sum()
    return (weights * values).sum()


def integrate(dataset, data_layer, target_band, funct, kwargs={}):
    mask = dataset.GetRasterBand(1).ReadAsArray() != 0

    # Create an array with the x co-ordinate of each grid point, and
    # one with the y co-ordinate of each grid point
    height, width = mask.shape
    x_left, x_step, d1, y_top, d2, y_step = dataset.GetGeoTransform()
    xcoords = np.arange(x_left + x_step / 2.0, x_left + x_step * width, x_step)
    ycoords = np.arange(y_top + y_step / 2.0, y_top + y_step * height, y_step)
    xarray, yarray = np.meshgrid(xcoords, ycoords)

    # Create a ufunc that makes the interpolation given the above arrays
    def interpolate_one_point(x, y, mask):
        if not mask:
            return np.nan
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)
        return funct(point, data_layer, **kwargs)

    interpolate = np.vectorize(interpolate_one_point, otypes=[np.float32])

    # Make the calculation
    result = interpolate(xarray, yarray, mask)
    result[np.isnan(result)] = NODATAVALUE
    target_band.SetNoDataValue(NODATAVALUE)
    target_band.WriteArray(result)


def create_ogr_layer_from_timeseries(filenames, epsg, data_source):
    # Prepare the co-ordinate transformation from WGS84 to epsg
    source_sr = osr.SpatialReference()
    source_sr.ImportFromEPSG(4326)
    target_sr = osr.SpatialReference()
    target_sr.ImportFromEPSG(epsg)
    transform = osr.CoordinateTransformation(source_sr, target_sr)

    layer = data_source.CreateLayer("stations", target_sr)
    layer.CreateField(ogr.FieldDefn("filename", ogr.OFTString))
    for filename in filenames:
        with open(filename) as f:
            ts = HTimeseries(f)
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(ts.location["abscissa"], ts.location["ordinate"])
        point.Transform(transform)
        f = ogr.Feature(layer.GetLayerDefn())
        f.SetGeometry(point)
        f.SetField("filename", filename)
        layer.CreateFeature(f)
    return layer


def _needs_calculation(output_filename, date, stations_layer):
    """
    Used by h_integrate to check whether the output file needs to be calculated
    or not. It does not need to be calculated if it already exists and has been
    calculated from all available data.
    """
    # Return immediately if output file does not exist
    if not os.path.exists(output_filename):
        return True

    # Get list of files which were used to calculate the output file
    fp = gdal.Open(output_filename)
    try:
        actual_input_files = fp.GetMetadataItem("INPUT_FILES")
        if actual_input_files is None:
            raise IOError(
                "{} does not contain the metadata item INPUT_FILES".format(
                    output_filename
                )
            )
    finally:
        fp = None  # Close file
    actual_input_files = set(actual_input_files.split("\n"))

    # Get list of files available for calculating the output file
    stations_layer.ResetReading()
    available_input_files = set(
        [
            station.GetField("filename")
            for station in stations_layer
            if os.path.exists(station.GetField("filename"))
        ]
    )

    # Which of these files have not been used?
    unused_files = available_input_files - actual_input_files

    # For each one of these files, check whether it has newly available data.
    # Upon finding one that does, the verdict is made: return True
    for filename in unused_files:
        with open(filename) as f:
            t = HTimeseries(f)
        try:
            value = t.data.loc[date, "value"]
            if not isnan(value):
                return True
        except KeyError:
            continue

    # We were unable to find data that had not already been used
    return False


def h_integrate(
    mask, stations_layer, date, output_filename_prefix, date_fmt, funct, kwargs
):
    date_fmt_for_filename = date.strftime(date_fmt).replace(" ", "-").replace(":", "-")
    output_filename = "{}-{}.tif".format(
        output_filename_prefix, date.strftime(date_fmt_for_filename)
    )
    if not _needs_calculation(output_filename, date, stations_layer):
        return

    # Read the time series values and add the 'value' attribute to
    # stations_layer
    stations_layer.CreateField(ogr.FieldDefn("value", ogr.OFTReal))
    input_files = []
    stations_layer.ResetReading()
    for station in stations_layer:
        filename = station.GetField("filename")
        with open(filename) as f:
            t = HTimeseries(f)
        try:
            value = t.data.loc[date, "value"]
        except KeyError:
            value = np.nan
        station.SetField("value", value)
        if not isnan(value):
            input_files.append(filename)
        stations_layer.SetFeature(station)
    if not input_files:
        return

    # Create destination data source
    output = gdal.GetDriverByName("GTiff").Create(
        output_filename, mask.RasterXSize, mask.RasterYSize, 1, gdal.GDT_Float32
    )
    output.SetMetadataItem("TIMESTAMP", date.strftime(date_fmt))
    output.SetMetadataItem("INPUT_FILES", "\n".join(input_files))

    try:
        # Set geotransform and projection in the output data source
        output.SetGeoTransform(mask.GetGeoTransform())
        output.SetProjection(mask.GetProjection())

        # Do the integration
        integrate(mask, stations_layer, output.GetRasterBand(1), funct, kwargs)
    finally:
        # Close the dataset
        output = None


def extract_point_from_raster(point, data_source, band_number=1):
    """Return floating-point value that corresponds to given point."""

    # Convert point co-ordinates so that they are in same projection as raster
    point_sr = point.GetSpatialReference()
    raster_sr = osr.SpatialReference()
    raster_sr.ImportFromWkt(data_source.GetProjection())
    transform = osr.CoordinateTransformation(point_sr, raster_sr)
    point.Transform(transform)

    # Convert geographic co-ordinates to pixel co-ordinates
    x, y = point.GetX(), point.GetY()
    forward_transform = Affine.from_gdal(*data_source.GetGeoTransform())
    reverse_transform = ~forward_transform
    px, py = reverse_transform * (x, y)
    px, py = int(px + 0.5), int(py + 0.5)

    # Extract pixel value
    band = data_source.GetRasterBand(band_number)
    structval = band.ReadRaster(px, py, 1, 1, buf_type=gdal.GDT_Float32)
    result = struct.unpack("f", structval)[0]
    if result == band.GetNoDataValue():
        result = float("nan")
    return result


def extract_point_timeseries_from_rasters(files, point):
    """Return time series of point values from a set of rasters.

    Arguments:
    files: Sequence or set of rasters.
    point: An OGR point.

    The rasters must have TIMESTAMP metadata item. The function reads all
    rasters, extracts the value at specified point, and returns all extracted
    values as a Timeseries object.
    """
    result = HTimeseries()
    for f in files:
        fp = gdal.Open(f)
        try:
            isostring = fp.GetMetadata()["TIMESTAMP"]
            timestamp = iso8601.parse_date(isostring, default_timezone=None)
            value = extract_point_from_raster(point, fp)
            result.data.loc[timestamp, "value"] = value
            result.data.loc[timestamp, "flags"] = ""
        finally:
            fp = None
    result.data = result.data.sort_index()
    return result
