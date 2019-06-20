# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time
import datetime
import pytz

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import force_text, override

from dashboards_app.models import Dashboards_appConfig
from cms import api
from cms.models import StaticPlaceholder

from . import Dashboards_appTestCase


class TestAppConfigPluginsBase(Dashboards_appTestCase):
    plugin_to_test = 'TextPlugin'
    plugin_params = {}

    def setUp(self):
        super(TestAppConfigPluginsBase, self).setUp()
        self.placeholder = self.plugin_page.placeholders.all()[0]
        api.add_plugin(
            self.placeholder, self.plugin_to_test, self.language,
            app_config=self.app_config, **self.plugin_params)
        self.plugin = self.placeholder.get_plugins()[0].get_plugin_instance()[0]
        self.plugin.save()
        self.plugin_page.publish(self.language)
        self.another_app_config = Dashboards_appConfig.objects.create(
            namespace=self.rand_str())


class TestPluginLanguageHelperMixin(object):
    def _test_plugin_languages_with_dashboard(self, dashboard):
        """Set up conditions to test plugin languages edge cases"""
        # Add 'de' translation to one of the dashboards
        title_de = 'title-de'
        title_en = dashboard.title
        dashboard.set_current_language('de')
        dashboard.title = title_de
        dashboard.save()

        # Unpublish page with dashboards_app apphook
        self.page.unpublish('en')
        cache.clear()
        response = self.client.get(self.plugin_page.get_absolute_url())

        # This dashboard should not be visible on 'en' page/plugin
        self.assertNotContains(response, title_en)


class TestArchivePlugin(TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appArchivePlugin'

    def test_archive_plugin(self):
        dates = [
            datetime.datetime(2014, 11, 15, 12, 0, 0, 0, pytz.UTC),
            datetime.datetime(2014, 11, 16, 12, 0, 0, 0, pytz.UTC),
            datetime.datetime(2015, 1, 15, 12, 0, 0, 0, pytz.UTC),
            datetime.datetime(2015, 1, 15, 12, 0, 0, 0, pytz.UTC),
            datetime.datetime(2015, 1, 15, 12, 0, 0, 0, pytz.UTC),
            datetime.datetime(2015, 2, 15, 12, 0, 0, 0, pytz.UTC),
        ]
        dashboards = []
        for d in dates:
            dashboard = self.create_dashboard(publishing_date=d)
            dashboards.append(dashboard)
        response = self.client.get(self.plugin_page.get_absolute_url())
        response_content = force_text(response.content)
        needle = '<a href="/en/page/{year}/{month}/"[^>]*>'
        '[^<]*<span class="badge">{num}</span>'
        month1 = needle.format(year=2014, month=11, num=2)
        month2 = needle.format(year=2015, month=2, num=1)
        month3 = needle.format(year=2015, month=1, num=3)
        self.assertRegexpMatches(response_content, month1)
        self.assertRegexpMatches(response_content, month2)
        self.assertRegexpMatches(response_content, month3)


class TestDashboardSearchPlugin(TestAppConfigPluginsBase):
    """Simply tests that the plugin form renders on the page."""
    # This is a really weak test. To do more, we'll have to submit the form,
    # yadda yadda yadda. Test_views.py should already test the other side of
    # this.
    plugin_to_test = 'Dashboards_appDashboardSearchPlugin'
    plugin_params = {
        "max_dashboards": 5,
    }

    def test_dashboard_search_plugin(self):
        needle = '<input type="hidden" name="max_dashboards" value="{num}">'
        response = self.client.get(self.plugin_page.get_absolute_url())
        self.assertContains(response, needle.format(num=5))


class TestAuthorsPlugin(TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appAuthorsPlugin'

    def test_authors_plugin(self):
        author1, author2 = self.create_person(), self.create_person()
        # Published, author1 dashboards in our current namespace
        author1_dashboards = []
        for _ in range(3):
            dashboard = self.create_dashboard(author=author1)
            author1_dashboards.append(dashboard)

        # Published, author2 dashboards in our current namespace
        other_dashboards = []
        for _ in range(5):
            dashboard = self.create_dashboard(author=author2)
            other_dashboards.append(dashboard)

        # Unpublished, author1 dashboards in our current namespace
        for _ in range(7):
            dashboard = self.create_dashboard(
                author=author1,
                is_published=False
            )
            other_dashboards.append(dashboard)

        # Published, author1 dashboards in a different namespace
        other_dashboards.append(self.create_dashboard(
            author=author1,
            app_config=self.another_app_config
        ))

        # REQUIRED DUE TO USE OF RAW QUERIES
        time.sleep(1)

        response = self.client.get(self.plugin_page.get_absolute_url())
        response_content = force_text(response.content)
        # This pattern tries to accommodate all the templates from all the
        # versions of this package.
        pattern = '<a href="{url}">\s*</a>'
        author1_pattern = pattern.format(
            url=reverse(
                '{0}:dashboard-list-by-author'.format(self.app_config.namespace),
                args=[author1.slug]
            )
        )
        author2_pattern = pattern.format(
            url=reverse(
                '{0}:dashboard-list-by-author'.format(self.app_config.namespace),
                args=[author2.slug]
            )
        )
        self.assertRegexpMatches(response_content, author1_pattern)
        self.assertRegexpMatches(response_content, author2_pattern)


class TestCategoriesPlugin(TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appCategoriesPlugin'

    def test_categories_plugin(self):
        # Published, category1 dashboards in our current namespace
        cat1_dashboards = []
        for _ in range(3):
            dashboard = self.create_dashboard()
            dashboard.categories.add(self.category1)
            cat1_dashboards.append(dashboard)

        # Published category2 dashboards in our namespace
        other_dashboards = []
        for _ in range(5):
            dashboard = self.create_dashboard()
            dashboard.categories.add(self.category2)
            other_dashboards.append(dashboard)

        # Some tag1, but unpublished dashboards
        for _ in range(7):
            dashboard = self.create_dashboard(is_published=False)
            dashboard.categories.add(self.category1)
            other_dashboards.append(dashboard)

        # Some tag1 dashboards in another namespace
        for _ in range(1):
            dashboard = self.create_dashboard(app_config=self.another_app_config)
            dashboard.categories.add(self.category1)
            other_dashboards.append(dashboard)

        # REQUIRED DUE TO USE OF RAW QUERIES
        time.sleep(1)

        response = self.client.get(self.plugin_page.get_absolute_url())
        response_content = force_text(response.content)
        # We use two different patterns in alternation because different
        # versions of dashboards_app have different templates
        pattern = '<span[^>]*>{num}</span>\s*<a href=[^>]*>{name}</a>'
        pattern += '|<a href=[^>]*>{name}</a>\s*<span[^>]*>{num}</span>'
        needle1 = pattern.format(num=3, name=self.category1.name)
        needle2 = pattern.format(num=5, name=self.category2.name)
        self.assertRegexpMatches(response_content, needle1)
        self.assertRegexpMatches(response_content, needle2)


class TestFeaturedDashboardsPlugin(TestPluginLanguageHelperMixin,
                                 TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appFeaturedDashboardsPlugin'
    plugin_params = {
        "dashboard_count": 5,
    }

    def test_featured_dashboards_plugin(self):
        featured_dashboards = [self.create_dashboard(
            is_featured=True,
            is_published=True
        ) for _ in range(3)]
        # Some featured dashboards but unpublished dashboards
        other_dashboards = [self.create_dashboard(
            is_featured=True,
            is_published=False
        ) for _ in range(3)]
        # Some non-featured dashboards in the same namespace
        other_dashboards += [self.create_dashboard() for _ in range(3)]
        # Some featured dashboards in another namespace
        other_dashboards += [self.create_dashboard(
            is_featured=True,
            app_config=self.another_app_config
        ) for _ in range(3)]

        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in featured_dashboards:
            self.assertContains(response, dashboard.title)
        for dashboard in other_dashboards:
            self.assertNotContains(response, dashboard.title)

    def test_featured_dashboards_plugin_unpublished_app_page(self):
        with override(self.language):
            dashboards = [self.create_dashboard(is_featured=True)
                        for _ in range(3)]

        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in dashboards:
            self.assertContains(response, dashboard.title)

        self.page.unpublish(self.language)
        self.reload_urls()
        cache.clear()
        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in dashboards:
            self.assertNotContains(response, dashboard.title)

    def test_featured_dashboards_plugin_language(self):
        dashboard = self.create_dashboard(is_featured=True)
        self._test_plugin_languages_with_dashboard(dashboard)


class TestLatestDashboardsPlugin(TestPluginLanguageHelperMixin,
                               TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appLatestDashboardsPlugin'
    plugin_params = {
        "latest_dashboards": 7,
    }

    def test_latest_dashboards_plugin(self):
        dashboards = [self.create_dashboard() for _ in range(7)]
        another_app_config = Dashboards_appConfig.objects.create(namespace='another')
        another_dashboards = [self.create_dashboard(app_config=another_app_config)
                            for _ in range(3)]
        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in dashboards:
            self.assertContains(response, dashboard.title)
        for dashboard in another_dashboards:
            self.assertNotContains(response, dashboard.title)

    def _test_latest_dashboards_plugin_exclude_count(self, exclude_count=0):
        self.plugin.exclude_featured = exclude_count
        self.plugin.save()
        self.plugin_page.publish(self.plugin.language)
        dashboards = []
        featured_dashboards = []
        for idx in range(7):
            if idx % 2:
                featured_dashboards.append(self.create_dashboard(is_featured=True))
            else:
                dashboards.append(self.create_dashboard())
        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in dashboards:
            self.assertContains(response, dashboard.title)
        # check that configured among of featured dashboards is excluded
        for featured_dashboard in featured_dashboards[:exclude_count]:
            self.assertNotContains(response, featured_dashboard.title)
        # ensure that other dashboards featured dashboards are present
        for featured_dashboard in featured_dashboards[exclude_count:]:
            self.assertContains(response, featured_dashboard.title)

    def test_latest_dashboards_plugin_exclude_featured(self):
        self._test_latest_dashboards_plugin_exclude_count(3)

    def test_latest_dashboards_plugin_no_excluded_featured(self):
        self._test_latest_dashboards_plugin_exclude_count()

    def test_latest_dashboards_plugin_unpublished_app_page(self):
        with override(self.language):
            dashboards = [self.create_dashboard() for _ in range(3)]

        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in dashboards:
            self.assertContains(response, dashboard.title)

        self.page.unpublish(self.language)
        self.reload_urls()
        cache.clear()
        response = self.client.get(self.plugin_page.get_absolute_url())
        for dashboard in dashboards:
            self.assertNotContains(response, dashboard.title)

    def test_latest_dashboards_plugin_language(self):
        dashboard = self.create_dashboard()
        self._test_plugin_languages_with_dashboard(dashboard)


class TestPrefixedLatestDashboardsPlugin(TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appLatestDashboardsPlugin'
    plugin_params = {
        "latest_dashboards": 7,
    }

    def setUp(self):
        super(TestPrefixedLatestDashboardsPlugin, self).setUp()
        self.app_config.template_prefix = 'dummy'
        self.app_config.save()

    def test_latest_dashboards_plugin(self):
        response = self.client.get(self.plugin_page.get_absolute_url())
        self.assertContains(response, 'This is dummy latest dashboards plugin')


class TestRelatedDashboardsPlugin(TestPluginLanguageHelperMixin,
                                Dashboards_appTestCase):

    def test_related_dashboards_plugin(self):
        main_dashboard = self.create_dashboard(app_config=self.app_config)
        static_placeholder = StaticPlaceholder.objects.get_or_create(
            code='dashboards_app_social',
            site__isnull=True,
        )[0]
        placeholder = static_placeholder.draft
        api.add_plugin(placeholder, 'Dashboards_appRelatedPlugin', self.language)

        static_placeholder.publish(None, language=self.language, force=True)

        plugin = placeholder.get_plugins()[0].get_plugin_instance()[0]
        plugin.save()

        self.plugin_page.publish(self.language)

        main_dashboard.save()
        for _ in range(3):
            a = self.create_dashboard()
            a.save()
            main_dashboard.related.add(a)

        another_language_dashboards = []
        with override('de'):
            for _ in range(4):
                a = self.create_dashboard()
                main_dashboard.related.add(a)
                another_language_dashboards.append(a)

        self.assertEquals(main_dashboard.related.count(), 7)
        unrelated = []
        for _ in range(5):
            unrelated.append(self.create_dashboard())

        response = self.client.get(main_dashboard.get_absolute_url())
        for dashboard in main_dashboard.related.all():
            self.assertContains(response, dashboard.title)
        for dashboard in unrelated:
            self.assertNotContains(response, dashboard.title)

        self.page.unpublish('de')
        self.reload_urls()
        cache.clear()
        response = self.client.get(main_dashboard.get_absolute_url())
        for dashboard in another_language_dashboards:
            self.assertNotContains(response, dashboard.title)

    def test_latest_dashboards_plugin_language(self):
        main_dashboard, related_dashboard = [
            self.create_dashboard() for _ in range(2)]
        main_dashboard.related.add(related_dashboard)
        self._test_plugin_languages_with_dashboard(related_dashboard)


class TestTagsPlugin(TestAppConfigPluginsBase):
    plugin_to_test = 'Dashboards_appTagsPlugin'

    def test_tags_plugin(self):
        # Published, tag1-tagged dashboards in our current namespace
        self.create_tagged_dashboards(3, tags=['tag1'])['tag1']
        other_dashboards = self.create_tagged_dashboards(5, tags=['tag2'])['tag2']
        # Some tag1, but unpublished dashboards
        other_dashboards += self.create_tagged_dashboards(
            7, tags=['tag1'], is_published=False)['tag1']
        # Some tag1 dashboards in another namespace
        other_dashboards += self.create_tagged_dashboards(
            1, tags=['tag1'], app_config=self.another_app_config)['tag1']

        # REQUIRED DUE TO USE OF RAW QUERIES
        time.sleep(1)

        response = self.client.get(self.plugin_page.get_absolute_url())
        response_content = force_text(response.content)
        self.assertRegexpMatches(response_content, 'tag1\s*<span[^>]*>3</span>')
        self.assertRegexpMatches(response_content, 'tag2\s*<span[^>]*>5</span>')
