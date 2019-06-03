""" Apps file for setting core package when app is ready
"""
from django.apps import AppConfig

import core_explore_example_app.permissions.discover as discover


class ExploreExampleAppConfig(AppConfig):
    """ Core application settings
    """
    name = 'core_explore_example_app'

    def ready(self):
        """ Runs when the app is ready

        Returns:

        """
        discover.init_permissions(self.apps)
