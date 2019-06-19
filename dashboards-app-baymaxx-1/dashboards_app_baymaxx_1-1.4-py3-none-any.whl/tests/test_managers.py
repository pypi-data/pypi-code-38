# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from dashboards_app.models import Dashboard

from . import Dashboards_appTestCase


class TestManagers(Dashboards_appTestCase):

    def test_published_dashboards_filtering(self):
        for i in range(5):
            self.create_dashboard()
        unpublised_dashboard = Dashboard.objects.first()
        unpublised_dashboard.is_published = False
        unpublised_dashboard.save()
        self.assertEqual(Dashboard.objects.published().count(), 4)
        self.assertNotIn(unpublised_dashboard, Dashboard.objects.published())

    # TODO: Should also test for publishing_date
    def test_view_dashboard_not_published(self):
        dashboard = self.create_dashboard(is_published=False)
        dashboard_url = dashboard.get_absolute_url()
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 404)
