# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.utils.timezone import now
from django.utils.translation import override

from dashboards_app.feeds import LatestDashboardsFeed, TagFeed, CategoryFeed

from . import Dashboards_appTestsMixin


class TestFeeds(Dashboards_appTestsMixin, TransactionTestCase):

    def test_latest_feeds(self):
        dashboard = self.create_dashboard()
        future_dashboard = self.create_dashboard(
            publishing_date=now() + timedelta(days=3),
            is_published=True,
        )
        url = reverse(
            '{0}:dashboard-list-feed'.format(self.app_config.namespace)
        )
        self.request = self.get_request('en', url)
        self.request.current_page = self.page
        feed = LatestDashboardsFeed()(self.request)

        self.assertContains(feed, dashboard.title)
        self.assertNotContains(feed, future_dashboard.title)

    def test_tag_feed(self):
        dashboards = self.create_tagged_dashboards()

        url = reverse(
            '{0}:dashboard-list-by-tag-feed'.format(self.app_config.namespace),
            args=['tag1']
        )
        self.request = self.get_request('en', url)
        if getattr(self.request, 'current_page', None) is None:
            self.request.current_page = self.page
        feed = TagFeed()(self.request, 'tag1')

        for dashboard in dashboards['tag1']:
            self.assertContains(feed, dashboard.title)
        for different_tag_dashboard in dashboards['tag2']:
            self.assertNotContains(feed, different_tag_dashboard.title)

    def test_category_feed(self):
        lang = self.category1.get_current_language()
        with override(lang):
            dashboard = self.create_dashboard()
            dashboard.categories.add(self.category1)
            different_category_dashboard = self.create_dashboard()
            different_category_dashboard.categories.add(self.category2)
            url = reverse(
                '{0}:dashboard-list-by-category-feed'.format(
                    self.app_config.namespace),
                args=[self.category1.slug]
            )
            self.request = self.get_request(lang, url)
            if getattr(self.request, 'current_page', None) is None:
                self.request.current_page = self.page

            feed = CategoryFeed()(self.request, self.category1.slug)

            self.assertContains(feed, dashboard.title)
            self.assertNotContains(feed, different_category_dashboard.title)
