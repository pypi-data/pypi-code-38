""" Core exporters apps config
"""
from django.apps import AppConfig
from core_exporters_app.exporters import discover
import core_exporters_app.components.exporter.watch as exporter_watch


# TODO: loaded two times (not a problem and may not happen in production) 
# see http://stackoverflow.com/a/16111968 
class CoreExportersAppConfig(AppConfig):
    """ Exporters configuration
    """
    name = 'core_exporters_app'
    verbose_name = "Core Exporters App Config"

    def ready(self):
        """ Run once at startup
        """
        discover.discover_exporter()
        exporter_watch.init()
