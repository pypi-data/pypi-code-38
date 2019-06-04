"""Resample inputs."""
import time
import argparse
import os
import sys
import glob
import logging

import numpy
from osgeo import gdal
import pygeoprocessing

gdal.SetCacheMax(2**30)


DEFAULT_GTIFF_CREATION_OPTIONS = (
    'TILED=YES', 'BIGTIFF=YES', 'COMPRESS=DEFLATE',
    'BLOCKXSIZE=256', 'BLOCKYSIZE=256')

logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s (%(relativeCreated)d) %(levelname)s %(name)s'
        ' [%(funcName)s:%(lineno)d] %(message)s'),
    stream=sys.stdout)
LOGGER = logging.getLogger(__name__)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description='Coarsen rasters.')
    parser.add_argument(
        '--factor', nargs='+', type=float, help='upscale factors',
        required=True)
    parser.add_argument(
        '--file_list', nargs='+', help='list of files/patterns to upscale',
        required=True)
    parser.add_argument(
        '--dest_path', type=str, help='destination path',
        required=True)

    args = parser.parse_args()
    print(args)

    try:
        LOGGER.info('making destination directory %s', args.dest_path)
        os.makedirs(args.dest_path[0])
    except OSError:
        LOGGER.info('%s already exists', args.dest_path)
        pass

    LOGGER.debug(args.file_list)
    for base_raster_path in [glob_path for pattern in args.file_list
                 for glob_path in glob.glob(pattern)]:
        LOGGER.info('processing %s', base_raster_path)
        base, ext = os.path.splitext(base_raster_path)
        for factor in args.factor:
            target_path = os.path.join(
                args.dest_path[0], '%s_%dx%s' % (
                    base, factor, ext))
            raster_info = pygeoprocessing.get_raster_info(base_raster_path)
            LOGGER.info('creating %s', target_path)

            # make a new raster that's / factor as big
            raster_x_size, raster_y_size = raster_info['raster_size']
            nodata = raster_info['nodata'][0]
            n_cols = int(raster_x_size / factor)
            n_rows = int(raster_y_size / factor)
            new_gt = list(raster_info['geotransform'])
            new_gt[1] *= factor
            new_gt[5] *= factor
            driver = gdal.GetDriverByName('GTiff')

            target_raster = driver.Create(
                target_path, n_cols, n_rows, 1, raster_info['datatype'],
                options=DEFAULT_GTIFF_CREATION_OPTIONS)
            target_raster.SetProjection(raster_info['projection'])
            target_raster.SetGeoTransform(new_gt)

            target_band = target_raster.GetRasterBand(1)
            target_band.SetNoDataValue(nodata)

            n_pixels = raster_x_size*raster_y_size
            processed_pixels = 0
            last_time = time.time()
            for offset_dict, data_array in pygeoprocessing.iterblocks(
                    (base_raster_path, 1)):
                processed_pixels += (
                    offset_dict['win_xsize'] * offset_dict['win_ysize'])
                current_time = time.time()
                if current_time > last_time + 5:
                    LOGGER.debug(
                        'row %d of %d\n pixel %d of %d\n%.2f%%',
                        offset_dict['yoff'], raster_y_size,
                        processed_pixels, n_pixels,
                        100*processed_pixels/n_pixels)
                    last_time = current_time

                nodata_mask = numpy.isclose(data_array, nodata)
                data_array[nodata_mask] = 0
                target_offset_dict = {
                    'xoff': int(offset_dict['xoff'] / factor),
                    'yoff': int(offset_dict['yoff'] / factor),
                    'win_xsize': int(
                        numpy.ceil(offset_dict['win_xsize'] / factor)),
                    'win_ysize': int(
                        numpy.ceil(offset_dict['win_xsize'] / factor)),
                }
                if (target_offset_dict['xoff'] +
                        target_offset_dict['win_xsize'] >= n_cols):
                    target_offset_dict['win_xsize'] = (
                        n_cols - target_offset_dict['xoff'])
                if (target_offset_dict['yoff'] +
                        target_offset_dict['win_ysize'] >= n_rows):
                    target_offset_dict['win_ysize'] = (
                        n_rows - target_offset_dict['yoff'])

                target_array = target_band.ReadAsArray(**target_offset_dict)
                result = numpy.zeros(target_array.shape)

                local_x_offset = int(
                    offset_dict['xoff']//factor*factor-offset_dict['xoff'])
                local_y_offset = int(
                    offset_dict['yoff']//factor*factor-offset_dict['yoff'])

                result = numpy.array([numpy.sum(data_array[
                        int(max(0, local_y_offset+factor*j)):
                        int(min(local_y_offset+factor*(j+1),
                                target_array.shape[0]))], axis=0)
                    for j in range(target_offset_dict['win_ysize'])])

                result = numpy.array([[
                    numpy.sum(result[
                        j, int(max(0, local_x_offset+factor*i)):
                              min(int(local_x_offset+factor*(i+1)),
                                  target_array.shape[1])])
                    for i in range(target_offset_dict['win_xsize'])]
                    for j in range(result.shape[0])])

                target_nodata_mask = numpy.isclose(target_array, nodata)
                try:
                    target_array[target_nodata_mask] = result[target_nodata_mask]
                except:
                    LOGGER.exception(
                        'target shape: %s, mask shape: %s, result shape: %s',
                        target_array.shape, target_nodata_mask.shape,
                        result.shape)
                    raise
                target_array[~target_nodata_mask] += result[~target_nodata_mask]
                target_band.WriteArray(
                    target_array,
                    xoff=target_offset_dict['xoff'],
                    yoff=target_offset_dict['yoff'])


if __name__ == '__main__':
    main()
