# -*- coding: utf-8 -*-
from django.utils.translation import activate

from dashboards_app.search_indexes import DashboardIndex

from . import Dashboards_appTestCase


class DashboardIndexingTests(Dashboards_appTestCase):

    def get_index(self):
        from haystack.constants import DEFAULT_ALIAS

        index = DashboardIndex()
        index._backend_alias = DEFAULT_ALIAS
        return index

    def test_dashboard_is_indexed_using_prepare(self):
        activate(self.language)

        lead_in = 'Hello! this text will be searchable.'

        dashboard = self.create_dashboard(lead_in=lead_in)
        # If set dashboards_app_UPDATE_SEARCH_DATA_ON_SAVE this will do
        # automatically
        dashboard.search_data = dashboard.get_search_data()

        index = self.get_index()

        data = index.prepare(dashboard)

        count = data['text'].count(lead_in)

        self.assertTrue(count != 0, "Couldn't find %s in text" % lead_in)

    def test_translated_dashboard_is_indexed_using_prepare(self):
        activate(self.language)

        lead_in = 'Hello! this text will be searchable.'

        # create english dashboard
        dashboard = self.create_dashboard(lead_in=lead_in)

        # create german translation for dashboard
        dashboard.set_current_language('de')
        dashboard.title = '%s [de]' % self.rand_str()
        dashboard.save()

        index = self.get_index()

        data = index.prepare(dashboard)

        self.assertEquals(data['language'], 'de')
        self.assertEquals(data['url'], dashboard.get_absolute_url('de'))

    def test_dashboard_not_indexed_if_no_translation(self):
        index = self.get_index()
        # create english dashboard
        dashboard = self.create_dashboard()

        # should the index be updated for this object? (yes)
        should_update = index.should_update(dashboard)
        self.assertEquals(should_update, True)

        # remove all translations for dashboard
        dashboard.translations.all().delete()

        # should the index be updated for this object? (no)
        should_update = index.should_update(dashboard)
        self.assertEquals(should_update, False)
