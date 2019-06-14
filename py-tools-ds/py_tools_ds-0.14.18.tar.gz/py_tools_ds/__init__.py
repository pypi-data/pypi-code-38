# -*- coding: utf-8 -*-
from __future__ import (division, print_function, absolute_import, unicode_literals)
from .version import __version__, __versionalias__   # noqa (E402 + F401)

__author__ = 'Daniel Scheffler'

# Validate GDAL version
try:
    import gdal
    import gdalnumeric
except ImportError:
    from osgeo import gdal
    from osgeo import gdalnumeric

try:
    getattr(gdal, 'Warp')
    getattr(gdal, 'Translate')
    getattr(gdalnumeric, 'OpenNumPyArray')
except AttributeError:
    import warnings
    warnings.warn("Your GDAL version is too old to support all functionalities of the 'py_tools_ds' package. "
                  "Please update GDAL!")
del gdal, gdalnumeric
