# -*- coding: utf-8 -*-

import os
import sys
import re

__author__ = "Daniel Scheffler"


def find_epsgfile():
    """Locate the proj.4 epsg file (defaults to '/usr/local/share/proj/epsg')."""
    try:
        epsgfile = os.environ['GDAL_DATA'].replace('/gdal', '/proj/epsg')
        assert os.path.exists(epsgfile)
    except (KeyError, AssertionError):
        try:
            from pyproj import __file__ as pyprojpath
            epsgfile = os.path.join(os.path.dirname(pyprojpath), 'data/epsg')
            assert os.path.exists(epsgfile)
        except (ImportError, AssertionError):
            epsgfile = '/usr/local/share/proj/epsg'
            if not os.path.exists(epsgfile):
                raise RuntimeError('Could not locate epsg file for converting WKT to EPSG code. '
                                   'Please make sure that your GDAL_DATA environment variable is properly set and the '
                                   'pyproj library is installed.')
    return epsgfile


def try2set_GDAL_DATA():
    """Try to set the 'GDAL_DATA' environment variable in case it is unset or invalid."""
    if 'GDAL_DATA' not in os.environ or not os.path.isdir(os.environ['GDAL_DATA']):
        is_anaconda = 'conda' in sys.version or 'Continuum' in sys.version or \
                      re.search('conda', sys.executable, re.I)
        if is_anaconda:
            if sys.platform in ['linux', 'linux2']:
                GDAL_DATA = os.path.join(os.path.dirname(sys.executable), "..", "share", "gdal")
            else:
                GDAL_DATA = os.path.join(os.path.dirname(sys.executable), "Library", "share", "gdal")
        else:
            GDAL_DATA = os.path.join("usr", "local", "share", "gdal") if sys.platform in ['linux', 'linux2'] else ''

        if os.path.isdir(GDAL_DATA):
            os.environ['GDAL_DATA'] = GDAL_DATA
