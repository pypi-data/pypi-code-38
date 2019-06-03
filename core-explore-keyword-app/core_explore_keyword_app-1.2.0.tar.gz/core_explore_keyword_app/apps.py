""" Apps file for setting core package when app is ready
"""
from django.apps import AppConfig

from core_explore_keyword_app.permissions import discover


class ExploreKeywordAppConfig(AppConfig):
    """ Core application settings
    """
    name = 'core_explore_keyword_app'

    def ready(self):
        """ Run when the app is ready.

        Returns:

        """
        discover.init_permissions(self.apps)
