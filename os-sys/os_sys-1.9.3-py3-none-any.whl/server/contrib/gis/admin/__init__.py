from server.contrib.admin import (
    HORIZONTAL, VERTICAL, AdminSite, ModelAdmin, StackedInline, TabularInline,
    autodiscover, register, site,
)
from server.contrib.gis.admin.options import GeoModelAdmin, OSMGeoAdmin
from server.contrib.gis.admin.widgets import OpenLayersWidget

__all__ = [
    'HORIZONTAL', 'VERTICAL', 'AdminSite', 'ModelAdmin', 'StackedInline',
    'TabularInline', 'autodiscover', 'register', 'site',
    'GeoModelAdmin', 'OSMGeoAdmin', 'OpenLayersWidget',
]
