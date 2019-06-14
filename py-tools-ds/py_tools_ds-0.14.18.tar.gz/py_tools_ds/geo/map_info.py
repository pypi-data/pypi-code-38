# -*- coding: utf-8 -*-
import re
import math
import warnings
import os
from typing import Union  # noqa F401  # flake8 issue

import numpy as np
try:
    from osgeo import osr
    from osgeo import gdal
except ImportError:
    # noinspection PyPackageRequirements
    import osr
    import gdal

from .coord_trafo import transform_any_prj
from .projection import get_proj4info, proj4_to_dict, isLocal

__author__ = "Daniel Scheffler"


class Geocoding(object):
    def __init__(self, mapinfo=None, gt=None, prj=''):
        # type: (Union[list, tuple], Union[list, tuple], str) -> None
        """Get an instance of the Geocoding object.

        :param mapinfo: ENVI map info, e.g., ['UTM', 1, 1, 192585.0, 5379315.0, 30.0, 30.0, 41, 'North', 'WGS-84']
        :param gt:      GDAL GeoTransform, e.g. (249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0)
        :param prj:     GDAL Projection - WKT Format
        """
        # FIXME this class only supports UTM and Geographic Lat/Lon projections
        self.prj_name = 'Arbitrary'
        self.ul_x_map = 0.
        self.ul_y_map = 0.
        self.ul_x_px = 1.
        self.ul_y_px = 1.
        self.gsd_x = 1.
        self.gsd_y = 1.
        self.rot_1_deg = 0.
        self.rot_1_rad = 0.
        self.rot_2_deg = 0.
        self.rot_2_rad = 0.
        self.utm_zone = 0
        self.utm_north_south = 'North'
        self.datum = ''
        self.units = ''

        if mapinfo:
            if gt or prj:
                warnings.warn("'gt' and 'prj' are not respected if mapinfo is given!")
            self.from_mapinfo(mapinfo)
        elif gt:
            self.from_geotransform_projection(gt, prj)

    def from_geotransform_projection(self, gt, prj):
        # type: (Union[list, tuple], str) -> 'Geocoding'
        """Create Geocoding object from GDAL GeoTransform + WKT projection string.

        HOW COMPUTATION OF RADIANTS WORKS:
        Building on top of the computation within self.to_geotransform():
        gt[1] = math.cos(rotation_rad) * gsd_x
        gt[2] = math.sin(rotation_rad) * gsd_x

        -> we have to solve this equation system to get rotation_rad:
        gsd_x = gt[2] / math.sin(rotation_rad)
        gt[1] = math.cos(rotation_rad) * gt[2] / math.sin(rotation_rad)
        gt[1] * math.sin(rotation_rad) = math.cos(rotation_rad) * gt[2]
        math.sin(rotation_rad) / math.cos(rotation_rad) = gt[2] / gt[1]
        math.tan(rotation_rad) = gt[2] / gt[1]
        rotation_rad = math.atan(gt[2] / gt[1])

        :param gt:  GDAL GeoTransform, e.g. (249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0)
        :param prj: GDAL Projection - WKT Format
        :return:    instance of Geocoding
        """
        if gt not in [None, [0, 1, 0, 0, 0, -1], (0, 1, 0, 0, 0, -1)]:
            # validate input geotransform
            if not isinstance(gt, (list, tuple)):
                raise TypeError("'gt' must be a list or a tuple. Received type %s." % type(gt))
            if len(gt) != 6:
                raise ValueError("'gt' must contain 6 elements.")

            self.ul_x_map = float(gt[0])
            self.ul_y_map = float(gt[3])

            # handle rotations
            if float(gt[2]) == 0:
                # no rotation. use default angles from init
                self.gsd_x = float(gt[1])
            else:
                self.rot_1_rad = math.atan(gt[2] / gt[1])
                self.rot_1_deg = math.degrees(self.rot_1_rad)
                self.gsd_x = gt[2] / math.sin(self.rot_1_rad)

            if float(gt[4]) == 0:
                # no rotation. use default angles from init
                self.gsd_y = float(abs(gt[5]))
            else:
                self.rot_2_rad = math.atan(gt[4] / gt[5])
                self.rot_2_deg = math.degrees(self.rot_2_rad)
                self.gsd_y = gt[4] / math.sin(self.rot_2_rad)

            # handle projection
            srs = osr.SpatialReference()
            srs.ImportFromWkt(prj)

            if isLocal(prj):
                self.prj_name = 'Arbitrary'
            else:
                # get prj_name and datum
                proj4 = proj4_to_dict(get_proj4info(proj=prj))  # type: dict
                self.prj_name = \
                    'Geographic Lat/Lon' if proj4['proj'] == 'longlat' else \
                    'UTM' if proj4['proj'] == 'utm' else proj4['proj']
                # FIXME there is no 'datum' key in case of, e.g., LAEA projection
                self.datum = 'WGS-84' if proj4['datum'] == 'WGS84' else proj4['datum']  # proj4['ellps']?
                self.units = proj4['unit'] if 'unit' in proj4 else self.units

                if self.prj_name == 'UTM':
                    self.utm_zone = srs.GetUTMZone()
                    self.utm_north_south = \
                        'North' if transform_any_prj(prj, 4326, self.ul_x_map, self.ul_y_map)[0] >= 0. else 'South'

            del srs

        return self

    def from_mapinfo(self, mapinfo):
        # type: (Union[list, tuple]) -> 'Geocoding'
        """Create Geocoding object from ENVI map info.

        :param mapinfo: ENVI map info, e.g., ['UTM', 1, 1, 192585.0, 5379315.0, 30.0, 30.0, 41, 'North', 'WGS-84']
        :return:        instance of Geocoding
        """
        if mapinfo:
            # validate input map info
            if not isinstance(mapinfo, (list, tuple)):
                raise TypeError("'mapinfo' must be a list or a tuple. Received type %s." % type(mapinfo))

            def assert_mapinfo_length(min_len):
                if len(mapinfo) < min_len:
                    raise ValueError("A map info of type '%s' must contain at least %s elements. Received %s."
                                     % (mapinfo[0], min_len, len(mapinfo)))

            assert_mapinfo_length(10 if mapinfo[0] == 'UTM' else 9 if mapinfo[0] == 'Arbitrary' else 8)

            # parse mapinfo
            self.prj_name = mapinfo[0]
            self.ul_x_px, self.ul_y_px, self.ul_x_map, self.ul_y_map, self.gsd_x = (float(i) for i in mapinfo[1:6])
            self.gsd_y = float(abs(mapinfo[6]))

            if self.prj_name == 'UTM':
                self.utm_zone = mapinfo[7]
                self.utm_north_south = mapinfo[8]
                self.datum = mapinfo[9]
            else:
                self.datum = mapinfo[7]

            # handle rotation
            for i in mapinfo:
                if isinstance(i, str) and re.search('rotation', i, re.I):
                    self.rot_1_deg = float(i.split('=')[1].strip())
                    self.rot_2_deg = self.rot_1_deg
                    self.rot_1_rad = math.radians(self.rot_1_deg)
                    self.rot_2_rad = math.radians(self.rot_2_deg)

        return self

    def to_geotransform(self):
        # type: () -> tuple
        """Return GDAL GeoTransform list using the attributes of the Geocoding instance.

        For equations, see:
         https://gis.stackexchange.com/questions/229952/rotate-envi-hyperspectral-imagery-with-gdal/229962

        :return:    GDAL GeoTransform, e.g. [249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0]
        """
        # handle pixel coordinates of UL unequal to (1/1)
        ul_map_x = self.ul_x_map if self.ul_x_px == 1 else (self.ul_x_map - (self.ul_x_px * self.gsd_x - self.gsd_x))
        ul_map_y = self.ul_y_map if self.ul_y_px == 1 else (self.ul_y_map - (self.ul_y_px * self.gsd_y - self.gsd_y))

        # handle rotation and pixel sizes
        gsd_x, rot_1 = (self.gsd_x, 0) if self.rot_1_deg == 0 else \
            (math.cos(self.rot_1_rad) * self.gsd_x, math.sin(self.rot_1_rad) * self.gsd_x)
        gsd_y, rot_2 = (self.gsd_y, 0) if self.rot_2_deg == 0 else \
            (math.cos(self.rot_2_rad) * self.gsd_y, math.sin(self.rot_2_rad) * self.gsd_y)

        return ul_map_x, gsd_x, rot_1, ul_map_y, rot_2, -gsd_y

    def to_mapinfo(self):
        """Return ENVI map info list using the attributes of the Geocoding instance.

        :return:    ENVI map info, e.g. [ UTM , 1 , 1 , 256785.0 , 4572015.0 , 30.0 , 30.0 , 43 , North , WGS-84 ]
        """
        mapinfo = [self.prj_name, self.ul_x_px, self.ul_y_px, self.ul_x_map, self.ul_y_map, self.gsd_x, abs(self.gsd_y)]

        # add UTM infos
        if self.prj_name in ['UTM', 'Arbitrary']:
            mapinfo.extend([self.utm_zone, self.utm_north_south])

        # add datum
        if self.prj_name != 'Arbitrary':
            mapinfo.append(self.datum)

        # add rotation
        if self.rot_1_deg != 0.:
            mapinfo.append('rotation=%.5f' % self.rot_1_deg)

        return mapinfo


def geotransform2mapinfo(gt, prj):
    # type: (Union[list, tuple, None], Union[str, None]) -> list
    """Builds an ENVI geo info from given GDAL GeoTransform and Projection (compatible with UTM and LonLat projections).
    :param gt:  GDAL GeoTransform, e.g. (249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0)
    :param prj: GDAL Projection - WKT Format
    :returns:   ENVI geo info, e.g. [ UTM , 1 , 1 , 256785.0 , 4572015.0 , 30.0 , 30.0 , 43 , North , WGS-84 ]
    :rtype:     list
    """
    try:
        return Geocoding(gt=gt, prj=prj).to_mapinfo()

    except KeyError:  # KeyError: 'datum' - in case of, e.g., ETRS/LAEA projection
        fn_bsq = "py_tools_ds__geotransform2mapinfo_temp.bsq"
        fn_hdr = os.path.splitext(fn_bsq)[0] + '.hdr'
        fdir = os.path.join(os.path.abspath(os.curdir))

        try:
            ds_out = gdal.GetDriverByName('ENVI').Create(fn_bsq, 2, 2, 1, gdal.GDT_Int32)
            ds_out.SetGeoTransform(gt)
            ds_out.SetProjection(prj)
            ds_out.FlushCache()
            del ds_out

            with open(fn_hdr, 'r') as inF:
                content = inF.read()
                if 'map info' in content:
                    res = re.search("map info = {(.*?)}", content, re.I).group(1)
                    map_info = [i.strip() for i in res.split(',')]

                    for i, ele in enumerate(map_info):
                        try:
                            map_info[i] = float(ele)
                        except ValueError:
                            pass
                else:
                    map_info = ['Arbitrary', 1.0, 1.0, 0.0, 0.0, 1.0, 1.0]

        finally:
            for fn in [fn_bsq, fn_hdr]:
                if os.path.exists(os.path.join(fdir, fn)):
                    gdal.Unlink(os.path.join(fdir, fn))

        return map_info


def mapinfo2geotransform(map_info):
    # type: (Union[list, None]) -> tuple
    """Builds GDAL GeoTransform tuple from an ENVI geo info.

    :param map_info: ENVI geo info (list), e.g., ['UTM', 1, 1, 192585.0, 5379315.0, 30.0, 30.0, 41, 'North', 'WGS-84']
    :returns:        GDAL GeoTransform, e.g. [249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0]
    """
    try:
        return Geocoding(mapinfo=map_info).to_geotransform()

    except (KeyError, ValueError):  # KeyError: 'datum' - in case of, e.g., ETRS/LAEA projection
        fn_bsq = "py_tools_ds__geotransform2mapinfo_temp.bsq"
        fn_hdr = os.path.splitext(fn_bsq)[0] + '.hdr'
        fdir = os.path.join(os.path.abspath(os.curdir))

        try:
            ds_out = gdal.GetDriverByName('ENVI').Create(fn_bsq, 2, 2, 1)
            ds_out.GetRasterBand(1).WriteArray(np.array([[1, 2], [2, 3]]))
            ds_out.FlushCache()
            del ds_out

            with open(fn_hdr, 'r') as InHdr:
                lines = InHdr.readlines()

            lines.append('map info = { %s }\n' % ', '.join([str(i) for i in map_info]))

            with open(fn_hdr, 'w') as OutHdr:
                OutHdr.writelines(lines)

            ds = gdal.Open(fn_bsq)
            gt = ds.GetGeoTransform()
            del ds

            return gt

        finally:
            for fn in [fn_bsq, fn_hdr]:
                if os.path.exists(os.path.join(fdir, fn)):
                    gdal.Unlink(os.path.join(fdir, fn))


def get_corner_coordinates(gdal_ds=None, gt=None, cols=None, rows=None):
    """Returns (ULxy, LLxy, LRxy, URxy) in the same coordinate units like the given geotransform."""
    assert gdal_ds or (gt and cols and rows), \
        "GEOP.get_corner_coordinates: Missing argument! Please provide either 'gdal_ds' or 'gt', 'cols' AND 'rows'."

    gdal_ds_GT = gdal_ds.GetGeoTransform() if gdal_ds else gt
    ext = []
    xarr = [0, gdal_ds.RasterXSize if gdal_ds else cols]
    yarr = [0, gdal_ds.RasterYSize if gdal_ds else rows]

    for px in xarr:
        for py in yarr:
            x = gdal_ds_GT[0] + (px * gdal_ds_GT[1]) + (py * gdal_ds_GT[2])
            y = gdal_ds_GT[3] + (px * gdal_ds_GT[4]) + (py * gdal_ds_GT[5])
            ext.append([x, y])
        yarr.reverse()
    del gdal_ds_GT

    return ext
