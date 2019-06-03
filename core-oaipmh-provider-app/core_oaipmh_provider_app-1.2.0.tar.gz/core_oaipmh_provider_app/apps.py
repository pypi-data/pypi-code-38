""" Apps file for setting oai-pmh when app is ready
"""
from django.apps import AppConfig

import core_oaipmh_provider_app.components.oai_provider_metadata_format.discover as discover_metadata_formats
import core_oaipmh_provider_app.components.oai_settings.discover as discover_settings
from core_oaipmh_provider_app.components.oai_data import watch as data_watch
from core_oaipmh_provider_app.tasks import insert_data_in_oai_data


class ProviderAppConfig(AppConfig):
    """ Core application settings
    """
    name = 'core_oaipmh_provider_app'

    def ready(self):
        """ Run when the app is ready

        Returns:

        """
        discover_settings.init()
        discover_metadata_formats.init()
        insert_data_in_oai_data()

        data_watch.init()
