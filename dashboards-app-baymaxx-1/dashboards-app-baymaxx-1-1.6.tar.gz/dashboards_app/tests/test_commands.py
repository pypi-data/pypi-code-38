# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management import call_command
from django.utils.translation import activate

from dashboards_app.models import Dashboard

from . import Dashboards_appTestCase


class TestCommands(Dashboards_appTestCase):

    def test_rebuild_search_data_command(self):
        # Just make sure we have a known language
        activate(self.language)

        dashboard = self.create_dashboard()

        search_data = dashboard.get_search_data(language=self.language)

        # make sure the search_data is empty
        # we avoid any handler that automatically sets the search_data
        dashboard.translations.filter(
            language_code=self.language).update(search_data='')

        # get fresh dashboard from db
        dashboard = Dashboard.objects.language(self.language).get(pk=dashboard.pk)

        # make sure search data is empty
        self.assertEqual(dashboard.search_data, '')
        # now run the command
        call_command('rebuild_dashboard_search_data', languages=[self.language])
        # now verify the dashboard's search_data has been updated.
        self.assertEqual(dashboard.search_data, search_data)
