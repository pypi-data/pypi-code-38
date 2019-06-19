# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import Dashboards_appTestCase
from dashboards_app.sitemaps import Dashboards_appSitemap

try:
    from django.contrib.sites.shortcuts import get_current_site
except ImportError:
    # Django 1.6
    from django.contrib.sites.models import get_current_site
from django.utils.translation import override


class TestSitemaps(Dashboards_appTestCase):

    def _sitemap_urls(self, sitemap):
        urls_info = sitemap.get_urls()
        urls = [url_info['location'] for url_info in urls_info]
        return urls

    def _dashboard_urls(self, dashboards, lang):
        self.request = self.get_request(lang)
        host = 'http://' + get_current_site(self.request).domain
        return [host + dashboard.get_absolute_url(lang) for dashboard in dashboards]

    def assertDashboardsIn(self, dashboards, sitemap):
        urls = self._sitemap_urls(sitemap)
        dashboard_urls = self._dashboard_urls(dashboards, sitemap.language)

        for url in dashboard_urls:
            self.assertIn(url, urls)

    def assertDashboardsNotIn(self, dashboards, sitemap):
        urls = self._sitemap_urls(sitemap)
        dashboard_urls = self._dashboard_urls(dashboards, sitemap.language)

        for url in dashboard_urls:
            self.assertNotIn(url, urls)

    def assertSitemapLanguage(self, sitemap, lang):
        self.request = self.get_request(lang)
        urls = self._sitemap_urls(sitemap)
        host = 'http://' + get_current_site(self.request).domain
        url_start = "{0}/{1}".format(host, lang)

        for url in urls:
            self.assertTrue(url.startswith(url_start))

    def test_listening_all_instances(self):
        dashboards = [self.create_dashboard() for _ in range(11)]
        unpublished_dashboard = dashboards[0]
        unpublished_dashboard.is_published = False
        unpublished_dashboard.save()
        sitemap = Dashboards_appSitemap()
        self.assertDashboardsIn(dashboards[1:], sitemap)
        self.assertDashboardsNotIn([unpublished_dashboard], sitemap)

    def test_listening_namespace(self):
        dashboards = [self.create_dashboard() for _ in range(11)]
        unpublished_dashboard = dashboards[0]
        unpublished_dashboard.is_published = False
        unpublished_dashboard.save()
        sitemap = Dashboards_appSitemap(namespace=self.app_config.namespace)
        self.assertDashboardsIn(dashboards[1:], sitemap)
        self.assertDashboardsNotIn([unpublished_dashboard], sitemap)

    def test_listening_unexisting_namespace(self):
        dashboards = [self.create_dashboard() for _ in range(11)]
        unpublished_dashboard = dashboards[0]
        unpublished_dashboard.is_published = False
        unpublished_dashboard.save()
        sitemap = Dashboards_appSitemap(
            namespace='not exists')
        self.assertFalse(sitemap.items())
        self.assertDashboardsNotIn(dashboards, sitemap)

    def test_languages_support(self):
        with override('en'):
            multilanguage_dashboard = self.create_dashboard()
            en_dashboard = self.create_dashboard()

        multilanguage_dashboard.create_translation(
            'de', title='DE title', slug='de-dashboard')
        with override('de'):
            de_dashboard = self.create_dashboard()

        en_sitemap = Dashboards_appSitemap(language='en')
        self.assertDashboardsIn([multilanguage_dashboard, en_dashboard], en_sitemap)
        self.assertDashboardsNotIn([de_dashboard], en_sitemap)
        self.assertSitemapLanguage(en_sitemap, 'en')

        de_sitemap = Dashboards_appSitemap(language='de')
        self.assertDashboardsIn([multilanguage_dashboard, de_dashboard], de_sitemap)
        self.assertDashboardsNotIn([en_dashboard], de_sitemap)
        self.assertSitemapLanguage(de_sitemap, 'de')
