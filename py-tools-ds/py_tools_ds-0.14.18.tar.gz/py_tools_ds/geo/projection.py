# -*- coding: utf-8 -*-

import re
import pyproj
from typing import Union  # noqa F401  # flake8 issue

# custom
try:
    from osgeo import osr
    from osgeo import gdal
except ImportError:
    import osr
    import gdal

from ..environment import gdal_env

__author__ = "Daniel Scheffler"


# try to set GDAL_DATA if unnot set or invalid
gdal_env.try2set_GDAL_DATA()


def get_proj4info(ds=None, proj=None):
    # type: (gdal.Dataset, Union[str, int]) -> str
    """Returns PROJ4 formatted projection info for the given gdal.Dataset or projection respectively,
    e.g. '+proj=utm +zone=43 +datum=WGS84 +units=m +no_defs '

    :param ds:      <gdal.Dataset> the gdal dataset to get PROJ4 info for
    :param proj:    <str,int> the projection to get PROJ4 formatted info for (WKT or 'epsg:1234' or <EPSG_int>)
    """
    assert ds or proj, "Specify at least one of the arguments 'ds' or 'proj'"
    srs = osr.SpatialReference()
    proj = ds.GetProjection() if ds else proj

    if isinstance(proj, str) and proj.startswith('epsg:'):
        proj = EPSG2WKT(int(proj.split(':')[1]))
    elif isinstance(proj, int):
        proj = EPSG2WKT(proj)

    srs.ImportFromWkt(proj)
    return srs.ExportToProj4()


def proj4_to_dict(proj4):
    # type: (str) -> dict
    """Converts a PROJ4-like string into a dictionary.
    :param proj4:   <str> the PROJ4-like string
    """
    items = [item for item in proj4.replace('+', '').split(' ') if '=' in item]
    return {k: v for k, v in [kv.split('=') for kv in items]}


def dict_to_proj4(proj4dict):
    # type: (dict) -> str
    """Converts a PROJ4-like dictionary into a PROJ4 string.
    :param proj4dict:   <dict> the PROJ4-like dictionary
    """
    return pyproj.Proj(proj4dict).srs


def proj4_to_WKT(proj4str):
    # type: (str) -> str
    """Converts a PROJ4-like string into a WKT string.
    :param proj4str:   <dict> the PROJ4-like string
    """
    srs = osr.SpatialReference()
    srs.ImportFromProj4(proj4str)
    return srs.ExportToWkt()


def prj_equal(prj1, prj2):
    # type: (Union[None, int, str], Union[None, int, str]) -> bool
    """Checks if the given two projections are equal.

    :param prj1: projection 1 (WKT or 'epsg:1234' or <EPSG_int>)
    :param prj2: projection 2 (WKT or 'epsg:1234' or <EPSG_int>)
    """
    if prj1 is None and prj2 is None or prj1 == prj2:
        return True
    else:
        return get_proj4info(proj=prj1) == get_proj4info(proj=prj2)


def isProjectedOrGeographic(prj):
    # type: (Union[str, int, dict]) -> Union[str, None]
    """

    :param prj: accepts EPSG, Proj4 and WKT projections
    """
    if prj is None:
        return None

    srs = osr.SpatialReference()
    if prj.startswith('EPSG:'):
        srs.ImportFromEPSG(int(prj.split(':')[1]))
    elif prj.startswith('+proj='):
        srs.ImportFromProj4(prj)
    elif prj.startswith('GEOGCS') or prj.startswith('PROJCS'):
        srs.ImportFromWkt(prj)
    else:
        raise RuntimeError('Unknown input projection.')

    return 'projected' if srs.IsProjected() else 'geographic' if srs.IsGeographic() else None


def isLocal(prj):
    # type: (Union[str, int, dict]) -> Union[bool, None]
    """

    :param prj: accepts EPSG, Proj4 and WKT projections
    """
    if not prj:
        return True

    srs = osr.SpatialReference()
    if prj.startswith('EPSG:'):
        srs.ImportFromEPSG(int(prj.split(':')[1]))
    elif prj.startswith('+proj='):
        srs.ImportFromProj4(prj)
    elif 'GEOGCS' in prj or 'PROJCS' in prj or 'LOCAL_CS' in prj:
        srs.ImportFromWkt(prj)
    else:
        raise RuntimeError('Unknown input projection: \n%s' % prj)

    return srs.IsLocal()


def EPSG2Proj4(EPSG_code):
    # type: (int) -> str
    if EPSG_code is not None:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(EPSG_code)
        proj4 = srs.ExportToProj4()

        if not proj4:
            raise EnvironmentError(gdal.GetLastErrorMsg())

        return proj4
    else:
        return ''


def EPSG2WKT(EPSG_code):
    # type: (int) -> str
    if EPSG_code is not None:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(EPSG_code)
        wkt = srs.ExportToWkt()

        if not wkt:
            raise EnvironmentError(gdal.GetLastErrorMsg())

        return wkt
    else:
        return ''


def WKT2EPSG(wkt, epsgfile=''):
    # type: (str, str) -> Union[int, None]
    """ Transform a WKT string to an EPSG code
    :param wkt:  WKT definition
    :param epsgfile: the proj.4 epsg file (automatically located if no path is provided)
    :returns:    EPSG code
    http://gis.stackexchange.com/questions/20298/is-it-possible-to-get-the-epsg-value-from-an-osr-spatialreference-class-using-th
    """
    # FIXME this function returns None if datum=NAD27 but works with datum=WGS84, e.g.:
    # FIXME {PROJCS["UTM_Zone_33N",GEOGCS["GCS_North_American_1927",DATUM["D_North_American_1927",SPHEROID
    # FIXME ["Clarke_1866",6378206.4,294.9786982]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],
    # FIXME PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],
    # FIXME PARAMETER["Central_Meridian",15.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],
    # FIXME UNIT["Meter",1.0]]}

    if not isinstance(wkt, str):
        raise TypeError("'wkt' must be a string. Received %s." % type(wkt))
    code = None  # default
    if not wkt:
        return None
    p_in = osr.SpatialReference()
    s = p_in.ImportFromWkt(wkt)
    if s == 5:  # invalid WKT
        raise Exception('Received an invalid WKT string: %s' % wkt)
    if p_in.IsLocal():
        raise Exception('The given WKT is a local coordinate system.')
    cstype = 'GEOGCS' if p_in.IsGeographic() else 'PROJCS'
    p_in.AutoIdentifyEPSG()
    an = p_in.GetAuthorityName(cstype)
    assert an in [None, 'EPSG'], "No EPSG code found. Found %s instead." % an
    ac = p_in.GetAuthorityCode(cstype)
    if ac is None:  # try brute force approach by grokking proj epsg definition file
        p_out = p_in.ExportToProj4()
        if p_out:
            epsgfile = epsgfile or gdal_env.find_epsgfile()
            with open(epsgfile) as f:
                for line in f:
                    if line.find(p_out) != -1:
                        m = re.search('<(\\d+)>', line)
                        if m:
                            code = m.group(1)
                            break
                code = int(code) if code else None  # match or no match
    else:
        code = int(ac)
    return code


def get_UTMzone(ds=None, prj=None):
    assert ds or prj, "Specify at least one of the arguments 'ds' or 'prj'"
    if isProjectedOrGeographic(prj) == 'projected':
        srs = osr.SpatialReference()
        srs.ImportFromWkt(ds.GetProjection() if ds else prj)
        return srs.GetUTMZone()
    else:
        return None


def get_prjLonLat(fmt='wkt'):
    # type: (str) -> Union[str, dict]
    """Returns standard geographic projection (EPSG 4326) in the WKT or PROJ4 format.
    :param fmt:     <str> target format - 'WKT' or 'PROJ4'
    """
    assert re.search('wkt', fmt, re.I) or re.search('Proj4', fmt, re.I), 'unsupported output format'
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out = srs.ExportToWkt() if re.search('wkt', fmt, re.I) else srs.ExportToProj4()

    if not out:
        raise EnvironmentError(gdal.GetLastErrorMsg())

    return out
