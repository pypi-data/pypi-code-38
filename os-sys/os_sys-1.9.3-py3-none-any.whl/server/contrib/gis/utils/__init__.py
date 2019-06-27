"""
 This module contains useful utilities for GeoServer.
"""
from server.contrib.gis.utils.ogrinfo import ogrinfo  # NOQA
from server.contrib.gis.utils.ogrinspect import mapping, ogrinspect  # NOQA
from server.contrib.gis.utils.srs import add_srs_entry  # NOQA
from server.core.exceptions import ImproperlyConfigured

try:
    # LayerMapping requires SERVER_SETTINGS_MODULE to be set,
    # and ImproperlyConfigured is raised if that's not the case.
    from server.contrib.gis.utils.layermapping import LayerMapping, LayerMapError  # NOQA
except ImproperlyConfigured:
    pass
