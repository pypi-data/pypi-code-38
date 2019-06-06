from server.apps import AppConfig
from server.core import serializers
from server.utils.translation import gettext_lazy as _


class GISConfig(AppConfig):
    name = 'server.contrib.gis'
    verbose_name = _("GIS")

    def ready(self):
        serializers.BUILTIN_SERIALIZERS.setdefault('geojson', 'server.contrib.gis.serializers.geojson')
