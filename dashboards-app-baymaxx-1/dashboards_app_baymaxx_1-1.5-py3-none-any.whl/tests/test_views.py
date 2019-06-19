# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from datetime import datetime, date
from operator import itemgetter
from random import randint

from django.conf import settings
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.timezone import now
from django.utils.translation import override

from dashboards_app.models import Dashboard, Dashboards_appConfig
from dashboards_app.search_indexes import DashboardIndex
from cms.utils.i18n import get_current_language, force_language
from easy_thumbnails.files import get_thumbnailer
from filer.models.imagemodels import Image
from parler.tests.utils import override_parler_settings
from parler.utils.conf import add_default_language_settings
from parler.utils.context import switch_language, smart_override

from . import Dashboards_appTestCase, TESTS_STATIC_ROOT

FEATURED_IMAGE_PATH = os.path.join(TESTS_STATIC_ROOT, 'featured_image.jpg')

PARLER_LANGUAGES_HIDE = {
    1: [
        {
            'code': u'en',
            'fallbacks': [u'de'],
            'hide_untranslated': True
        },
        {
            'code': u'de',
            'fallbacks': [u'en'],
            'hide_untranslated': True
        },
        {
            'code': u'fr',
            'fallbacks': [u'en'],
            'hide_untranslated': True
        },
    ],
    'default': {
        'hide_untranslated': True,
        'fallbacks': [],
    }
}

PARLER_LANGUAGES_SHOW = {
    1: [
        {
            'code': u'en',
            'fallbacks': [u'de'],
            'hide_untranslated': False
        },
        {
            'code': u'de',
            'fallbacks': [u'en'],
            'hide_untranslated': False
        },
        {
            'code': u'fr',
            'fallbacks': [u'en'],
            'hide_untranslated': False
        },
    ],
    'default': {
        'hide_untranslated': False,
        'fallbacks': [],
    }
}


class TestViews(Dashboards_appTestCase):

    def test_dashboards_list(self):
        namespace = self.app_config.namespace
        dashboards = [self.create_dashboard() for _ in range(11)]
        unpublished_dashboard = dashboards[0]
        unpublished_dashboard.is_published = False
        unpublished_dashboard.save()
        response = self.client.get(
            reverse('{0}:dashboard-list'.format(namespace)))
        for dashboard in dashboards[1:]:
            self.assertContains(response, dashboard.title)
        self.assertNotContains(response, unpublished_dashboard.title)

    def test_dashboards_list_exclude_featured(self):
        namespace = self.app_config.namespace
        # configure app config
        exclude_count = 2
        self.app_config.exclude_featured = exclude_count
        self.app_config.paginate_by = 2
        self.app_config.save()
        # set up dashboards
        dashboards = []
        featured_dashboards = []
        for idx in range(6):
            if idx % 2:
                featured_dashboards.append(self.create_dashboard(is_featured=True))
            else:
                dashboards.append(self.create_dashboard())
        # imitate ordering by publish date DESC
        dashboards.reverse()
        featured_dashboards.reverse()
        # prepare urls
        list_base_url = reverse('{0}:dashboard-list'.format(namespace))
        page_url_template = '{0}?page={1}'
        response_page_1 = self.client.get(list_base_url)
        response_page_2 = self.client.get(
            page_url_template.format(list_base_url, 2))

        # page 1
        # ensure that first two not featured dashboards are present on first page
        for dashboard in dashboards[:2]:
            self.assertContains(response_page_1, dashboard.title)
        # Ensure no featured dashboards are present on first page.
        for featured_dashboard in featured_dashboards[:2]:
            self.assertNotContains(response_page_1, featured_dashboard.title)

        # page 2
        # check that not excluded featured dashboard is present on second page
        for featured_dashboard in featured_dashboards[2:]:
            self.assertContains(response_page_2, featured_dashboard.title)
        # ensure that third not featured dashboard is present in the response
        for dashboard in dashboards[2:]:
            self.assertContains(response_page_2, dashboard.title)

    def test_dashboards_list_pagination(self):
        namespace = self.app_config.namespace
        paginate_by = self.app_config.paginate_by
        dashboards = [self.create_dashboard(
            app_config=self.app_config,
            publishing_date=datetime(2000 - i, 1, 1, 1, 1)
        ) for i in range(paginate_by + 5)]

        response = self.client.get(
            reverse('{0}:dashboard-list'.format(namespace)))
        for dashboard in dashboards[:paginate_by]:
            self.assertContains(response, dashboard.title)
        for dashboard in dashboards[paginate_by:]:
            self.assertNotContains(response, dashboard.title)

        response = self.client.get(
            reverse('{0}:dashboard-list'.format(namespace)) + '?page=2')
        for dashboard in dashboards[:paginate_by]:
            self.assertNotContains(response, dashboard.title)
        for dashboard in dashboards[paginate_by:]:
            self.assertContains(response, dashboard.title)

    def test_dashboards_by_author(self):
        author1, author2 = self.create_person(), self.create_person()
        for author in (author1, author2):
            dashboards = [
                self.create_dashboard(author=author) for _ in range(11)]
            response = self.client.get(reverse(
                'dashboards_app:dashboard-list-by-author',
                kwargs={'author': author.slug}))
            for dashboard in dashboards:
                self.assertContains(response, dashboard.title)

    def test_dashboards_by_unknown_author(self):
        response = self.client.get(reverse(
            'dashboards_app:dashboard-list-by-author',
            kwargs={'author': 'unknown'}))
        self.assertEqual(response.status_code, 404)

    def test_dashboards_by_category(self):
        """
        Tests that we can find dashboards by their categories, in ANY of the
        languages they are translated to.
        """
        LANGUAGES = add_default_language_settings(PARLER_LANGUAGES_HIDE)
        with override_parler_settings(PARLER_LANGUAGES=LANGUAGES):
            author = self.create_person()
            for category in (self.category1, self.category2):
                dashboards = []
                code = "{0}-".format(self.language)
                for _ in range(11):
                    dashboard = Dashboard.objects.create(
                        title=self.rand_str(),
                        slug=self.rand_str(prefix=code),
                        app_config=self.app_config,
                        author=author,
                        owner=author.user,
                        publishing_date=now(),
                        is_published=True,
                    )
                    # Make sure there are translations in place for the
                    # dashboards.
                    for language, _ in settings.LANGUAGES[1:]:
                        with switch_language(dashboard, language):
                            code = "{0}-".format(language)
                            dashboard.title = self.rand_str(prefix=code)
                            dashboard.save()

                    dashboard.categories.add(category)
                    dashboards.append(dashboard)

                for language, _ in settings.LANGUAGES:
                    with switch_language(category, language):
                        url = reverse(
                            'dashboards_app:dashboard-list-by-category',
                            kwargs={'category': category.slug})
                        response = self.client.get(url)
                    for dashboard in dashboards:
                        if language in dashboard.get_available_languages():
                            dashboard.set_current_language(language)
                            self.assertContains(response, dashboard.title)
                        else:
                            dashboard.set_current_language(language)
                            self.assertNotContains(response, dashboard.title)

    def test_dashboards_by_unknown_category(self):
        response = self.client.get(reverse(
            'dashboards_app:dashboard-list-by-category',
            kwargs={'category': 'unknown'}))
        self.assertEqual(response.status_code, 404)


class TestTemplatePrefixes(Dashboards_appTestCase):

    def setUp(self):
        super(TestTemplatePrefixes, self).setUp()
        self.app_config.template_prefix = 'dummy'
        self.app_config.save()

    def test_dashboards_list(self):
        namespace = self.app_config.namespace
        response = self.client.get(
            reverse('{0}:dashboard-list'.format(namespace)))
        self.assertContains(response, 'This is dummy dashboard list page')

    def test_dashboard_detail(self):
        dashboard = self.create_dashboard(app_config=self.app_config)
        namespace = self.app_config.namespace
        response = self.client.get(
            reverse(
                '{0}:dashboard-detail'.format(namespace),
                kwargs={'slug': dashboard.slug}
            ))
        self.assertContains(response, 'This is dummy dashboard detail page')


class TestTranslationFallbacks(Dashboards_appTestCase):
    def test_dashboard_detail_not_translated_fallback(self):
        """
        If the fallback is configured, dashboard is available in any
        (configured) language
        """
        author = self.create_person()
        code = "{0}-".format(self.language)

        with override(settings.LANGUAGES[0][0]):
            dashboard = Dashboard.objects.create(
                title=self.rand_str(),
                slug=self.rand_str(prefix=code),
                app_config=self.app_config,
                author=author, owner=author.user,
                publishing_date=now(),
                is_published=True,
            )
            dashboard.save()
            dashboard.categories.add(self.category1)
            url_one = reverse(
                'dashboards_app:dashboard-detail',
                kwargs={'slug': dashboard.slug}
            )
        # Parler settings should be same as cms settings and vice versa
        # ensure that if hide_untranslated = True we don't have a fallback
        # redirect.
        LANGUAGES = add_default_language_settings(PARLER_LANGUAGES_HIDE)
        with override_parler_settings(PARLER_LANGUAGES=LANGUAGES):
            language = settings.LANGUAGES[1][0]
            with switch_language(dashboard, language):
                slug = dashboard.safe_translation_getter('slug', None,
                    language_code=language, any_language=True)
                url = reverse(
                    'dashboards_app:dashboard-detail',
                    kwargs={'slug': slug}
                )
                self.assertNotEquals(url, url_one)
                response = self.client.get(url)
                self.assertEquals(response.status_code, 404)

            # Test again with redirect_on_fallback = False
            with self.settings(CMS_LANGUAGES=self.NO_REDIRECT_CMS_SETTINGS):
                language = settings.LANGUAGES[1][0]
                with switch_language(dashboard, language):
                    slug = dashboard.safe_translation_getter('slug', None)
                    url = reverse(
                        'dashboards_app:dashboard-detail',
                        kwargs={'slug': slug, }
                    )
                    self.assertNotEquals(url, url_one)
                    response = self.client.get(url)
                    self.assertEquals(response.status_code, 404)

    def test_dashboard_detail_not_translated_no_fallback(self):
        """
        If the fallback is disabled, dashboard is available only in the
        language in which is translated
        """
        author = self.create_person()
        code = "{0}-".format(self.language)
        dashboard = Dashboard.objects.create(
            title=self.rand_str(), slug=self.rand_str(prefix=code),
            app_config=self.app_config,
            author=author, owner=author.user,
            publishing_date=now(),
            is_published=True,
        )
        dashboard.save()
        dashboard.categories.add(self.category1)

        PARLER_LANGUAGES = {
            1: (
                {'code': 'de'},
                {'code': 'fr'},
                {'code': 'en'},
            ),
            'default': {
                'hide_untranslated': True,
            }
        }
        LANGUAGES = add_default_language_settings(PARLER_LANGUAGES)
        with override_parler_settings(PARLER_LANGUAGES=LANGUAGES):

            # current language - it still exists
            dashboard = Dashboard.objects.get(pk=dashboard.pk)
            language = settings.LANGUAGES[0][0]
            with switch_language(self.category1, language):
                url = reverse('dashboards_app:dashboard-detail',
                              kwargs={'slug': dashboard.slug})
                response = self.client.get(url)
                self.assertContains(response, dashboard.title)

            # non existing language - it does NOT exists
            language = settings.LANGUAGES[1][0]
            with switch_language(self.category1, language):
                url = reverse('dashboards_app:dashboard-detail',
                              kwargs={'slug': dashboard.slug})
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)


class TestImages(Dashboards_appTestCase):
    def test_dashboard_detail_show_featured_image(self):
        author = self.create_person()
        with open(FEATURED_IMAGE_PATH, 'rb') as f:
            file_obj = DjangoFile(f, name='featured_image.jpg')
            image = Image.objects.create(owner=author.user,
                                         original_filename='featured_image.jpg',
                                         file=file_obj,
                                         subject_location='fooobar')
        dashboard = self.create_dashboard(author=author, featured_image=image)
        response = self.client.get(dashboard.get_absolute_url())
        image_url = get_thumbnailer(dashboard.featured_image).get_thumbnail({
            'size': (800, 450),
            'crop': True,
            'subject_location': dashboard.featured_image.subject_location
        }).url
        self.assertContains(response, image_url)


class TestVariousViews(Dashboards_appTestCase):
    def test_dashboards_by_tag(self):
        """
        Tests that TagDashboardList view properly filters dashboards by their tags.

        This uses ANY of the languages dashboards are translated to.
        """

        untagged_dashboards = []
        for _ in range(5):
            dashboard = self.create_dashboard()
            untagged_dashboards.append(dashboard)

        dashboards = self.create_tagged_dashboards(
            3, tags=(self.rand_str(), self.rand_str()))

        # tags are created in previous loop on demand, we need their slugs
        tag_slug1, tag_slug2 = dashboards.keys()
        url = reverse('dashboards_app:dashboard-list-by-tag',
                      kwargs={'tag': tag_slug2})
        response = self.client.get(url)
        for dashboard in dashboards[tag_slug2]:
            self.assertContains(response, dashboard.title)
        for dashboard in dashboards[tag_slug1]:
            self.assertNotContains(response, dashboard.title)
        for dashboard in untagged_dashboards:
            self.assertNotContains(response, dashboard.title)

    def test_dashboards_by_unknown_tag(self):
        response = self.client.get(reverse(
            'dashboards_app:dashboard-list-by-tag',
            kwargs={'tag': 'unknown'}))
        self.assertEqual(response.status_code, 404)

    def test_dashboards_count_by_month(self):
        months = [
            {'date': date(1914, 7, 3), 'num_dashboards': 1},
            {'date': date(1914, 8, 3), 'num_dashboards': 3},
            {'date': date(1945, 9, 3), 'num_dashboards': 5},
        ]
        for month in months:
            for _ in range(month['num_dashboards']):
                dashboard = self.create_dashboard(publishing_date=month['date'])

        # unpublish one specific dashboard to test that it is not counted
        dashboard.is_published = False
        dashboard.save()
        months[-1]['num_dashboards'] -= 1

        self.assertEquals(
            sorted(
                Dashboard.objects.get_months(
                    request=None, namespace=self.app_config.namespace
                ), key=itemgetter('num_dashboards')), months)

    def test_dashboards_count_by_author(self):
        authors = []
        for num_dashboards in [1, 3, 5]:
            person = self.create_person()
            person.num_dashboards = num_dashboards
            authors.append((person, num_dashboards))

        for i, data in enumerate(authors):
            for _ in range(data[1]):
                dashboard = self.create_dashboard(author=data[0])
            # replace author with it's pk, as we need it to easily compare
            authors[i] = (data[0].pk, data[1])

        # unpublish one specific dashboard to test that it is not counted
        dashboard.is_published = False
        dashboard.save()
        authors[-1] = (authors[-1][0], authors[-1][1] - 1)

        self.assertEquals(
            sorted(
                Dashboard.objects.get_authors(
                    namespace=self.app_config.namespace).values_list(
                        'pk', 'num_dashboards'),
                key=itemgetter(1)),
            authors)

    def test_dashboards_count_by_tags(self):
        tags = Dashboard.objects.get_tags(
            request=None, namespace=self.app_config.namespace)
        self.assertEquals(tags, [])

        untagged_dashboards = []
        for _ in range(5):
            dashboard = self.create_dashboard()
            untagged_dashboards.append(dashboard)

        # Tag objects are created on attaching tag name to Dashboard,
        # so this looks not very DRY
        tag_names = ('tag foo', 'tag bar', 'tag buzz')
        # create unpublished dashboard to test that it is not counted
        self.create_tagged_dashboards(
            1, tags=(tag_names[0],), is_published=False)
        tag_slug2 = list(self.create_tagged_dashboards(
            3, tags=(tag_names[1],)).keys())[0]
        tag_slug3 = list(self.create_tagged_dashboards(
            5, tags=(tag_names[2],)).keys())[0]
        tags_expected = [
            (tag_slug3, 5),
            (tag_slug2, 3),
        ]
        tags = Dashboard.objects.get_tags(
            request=None, namespace=self.app_config.namespace)
        tags = [(tag.slug, tag.num_dashboards) for tag in tags]
        self.assertEquals(tags, tags_expected)

    def test_dashboards_by_date(self):
        in_dashboards = [
            self.create_dashboard(
                publishing_date=datetime(
                    1914, 7, 28, randint(0, 23), randint(0, 59)))
            for _ in range(11)]
        out_dashboards = [
            self.create_dashboard(
                publishing_date=datetime(
                    1939, 9, 1, randint(0, 23), randint(0, 59)))
            for _ in range(11)]
        response = self.client.get(reverse(
            'dashboards_app:dashboard-list-by-day',
            kwargs={'year': '1914', 'month': '07', 'day': '28'}))
        for dashboard in out_dashboards:
            self.assertNotContains(response, dashboard.title)
        for dashboard in in_dashboards:
            self.assertContains(response, dashboard.title)

    def test_dashboards_by_month(self):
        in_dashboards = [
            self.create_dashboard(
                publishing_date=datetime(
                    1914, 7, randint(1, 31), randint(0, 23), randint(0, 59)))
            for _ in range(11)]
        out_dashboards = [
            self.create_dashboard(
                publishing_date=datetime(
                    1939, 9, 1, randint(0, 23), randint(0, 59)))
            for _ in range(11)]
        response = self.client.get(reverse(
            'dashboards_app:dashboard-list-by-month',
            kwargs={'year': '1914', 'month': '07'}))
        for dashboard in out_dashboards:
            self.assertNotContains(response, dashboard.title)
        for dashboard in in_dashboards:
            self.assertContains(response, dashboard.title)

    def test_dashboards_by_year(self):
        in_dashboards = [
            self.create_dashboard(
                publishing_date=datetime(
                    1914, randint(1, 11), randint(1, 28),
                    randint(0, 23), randint(0, 59)))
            for _ in range(11)]
        out_dashboards = [
            self.create_dashboard(
                publishing_date=datetime(
                    1939, randint(1, 12), randint(1, 28),
                    randint(0, 23), randint(0, 59)))
            for _ in range(11)]
        response = self.client.get(reverse(
            'dashboards_app:dashboard-list-by-year', kwargs={'year': '1914'}))
        for dashboard in out_dashboards:
            self.assertNotContains(response, dashboard.title)
        for dashboard in in_dashboards:
            self.assertContains(response, dashboard.title)

    def test_unattached_namespace(self):
        # create a new namespace that has no corresponding blog app page
        app_config = Dashboards_appConfig.objects.create(namespace='another')
        dashboards = [self.create_dashboard(app_config=app_config)
                    for _ in range(11)]
        with self.assertRaises(NoReverseMatch):
            self.client.get(dashboards[0].get_absolute_url())


class TestIndex(Dashboards_appTestCase):
    def test_index_simple(self):
        self.request = self.get_request('en')
        self.index = DashboardIndex()
        content0 = self.rand_str(prefix='content0_')
        self.setup_categories()

        dashboard = self.create_dashboard(content=content0, lead_in='lead in text',
                                      title='a title')
        dashboard.categories.add()
        for tag_name in ('tag 1', 'tag2'):
            dashboard.tags.add(tag_name)
        for category in (self.category1, self.category2):
            dashboard.categories.add(category)
        dashboard.update_search_on_save = True
        dashboard.save()

        self.assertEqual(self.index.get_title(dashboard), 'a title')
        self.assertEqual(self.index.get_description(dashboard), 'lead in text')
        self.assertTrue('lead in text' in self.index.get_search_data(
            dashboard, 'en', self.request))
        self.assertTrue(content0 in self.index.get_search_data(
            dashboard, 'en', self.request))
        self.assertTrue('tag 1' in self.index.get_search_data(
            dashboard, 'en', self.request))
        self.assertTrue(self.category1.name in self.index.get_search_data(
            dashboard, 'en', self.request))

    def test_index_multilingual(self):
        self.index = DashboardIndex()
        content0 = self.rand_str(prefix='content0_')
        self.setup_categories()

        dashboard_1 = self.create_dashboard(
            content=content0, lead_in=u'lead in text', title=u'a title')
        dashboard_2 = self.create_dashboard(
            content=content0, lead_in=u'lead in text', title=u'second title')
        for dashboard in (dashboard_1, dashboard_2):
            for tag_name in ('tag 1', 'tag2'):
                dashboard.tags.add(tag_name)
            for category in (self.category1, self.category2):
                dashboard.categories.add(category)
        with switch_language(dashboard_2, 'de'):
            dashboard_2.title = u'de title'
            dashboard_2.lead_in = u'de lead in'
            dashboard_2.save()

        LANGUAGES = add_default_language_settings(PARLER_LANGUAGES_HIDE)
        with override_parler_settings(PARLER_LANGUAGES=LANGUAGES):
            with smart_override('de'):
                language = get_current_language()
                # english-only dashboard is excluded
                qs = self.index.index_queryset(language)
                self.assertEqual(qs.count(), 1)
                self.assertEqual(
                    qs.translated(language, title__icontains='title').count(),
                    1
                )
                # the language is correctly setup
                for dashboard_de in qs:
                    self.assertEqual(
                        self.index.get_title(dashboard_de), 'de title')
                    self.assertEqual(
                        self.index.get_description(dashboard_de), 'de lead in')


class ViewLanguageFallbackMixin(object):
    view_name = None
    view_kwargs = {}

    def get_view_kwargs(self):
        """
        Prepare and return kwargs to resolve view
        :return: dict
        """
        return {}.update(self.view_kwargs)

    def create_authors(self):
        self.author = self.create_person()
        self.owner = self.author.user
        return self.author, self.owner

    def create_de_dashboard(self, author=None, owner=None, app_config=None,
                          categories=None):
        if author is None:
            author = self.author
        if owner is None:
            owner = self.owner
        if app_config is None:
            app_config = self.app_config

        with force_language('de'):
            de_dashboard = Dashboard.objects.create(
                title='a DE title',
                slug='a-de-title',
                lead_in='DE lead in text',
                author=author,
                owner=owner,
                app_config=app_config,
                publishing_date=now(),
                is_published=True,
            )
        if categories:
            de_dashboard.categories = categories
        de_dashboard.tags.add('tag1')
        de_dashboard.save()
        return de_dashboard

    def create_en_dashboards(self, author=None, owner=None, app_config=None,
                           amount=3, categories=None):
        if author is None:
            author = self.author
        if owner is None:
            owner = self.owner
        if app_config is None:
            app_config = self.app_config

        with force_language('en'):
            dashboards = []
            for _ in range(amount):
                dashboard = self.create_dashboard(author=author,
                                              owner=owner,
                                              app_config=app_config)
                if categories:
                    dashboard.categories = categories
                dashboard.tags.add('tag1')
                dashboard.save()
                dashboards.append(dashboard)
        return dashboards

    def test_a0_en_only(self):
        namespace = self.app_config.namespace
        self.page.unpublish('de')
        author, owner = self.create_authors()
        author.translations.create(
            slug='{0}-de'.format(author.slug),
            language_code='de')
        de_dashboard = self.create_de_dashboard(
            author=author,
            owner=owner,
            categories=[self.category1],
        )
        dashboards = self.create_en_dashboards(categories=[self.category1])
        with force_language('en'):
            response = self.client.get(
                reverse(
                    '{0}:{1}'.format(namespace, self.view_name),
                    kwargs=self.get_view_kwargs()
                )
            )
        for dashboard in dashboards:
            self.assertContains(response, dashboard.title)
        self.assertNotContains(response, de_dashboard.title)

    def test_a1_en_de(self):
        namespace = self.app_config.namespace
        author, owner = self.create_authors()
        author.translations.create(
            slug='{0}-de'.format(author.slug),
            language_code='de')
        de_dashboard = self.create_de_dashboard(
            author=author,
            owner=owner,
            categories=[self.category1]
        )
        dashboards = self.create_en_dashboards(categories=[self.category1])
        with force_language('en'):
            response = self.client.get(
                reverse(
                    '{0}:{1}'.format(namespace, self.view_name),
                    kwargs=self.get_view_kwargs()
                )
            )
        for dashboard in dashboards:
            self.assertContains(response, dashboard.title)
        self.assertContains(response, de_dashboard.title)


class DashboardListViewLanguageFallback(ViewLanguageFallbackMixin,
                                      Dashboards_appTestCase):
    view_name = 'dashboard-list'


class LatestDashboardsFeedLanguageFallback(ViewLanguageFallbackMixin,
                                         Dashboards_appTestCase):
    view_name = 'dashboard-list-feed'


class YearDashboardListLanguageFallback(ViewLanguageFallbackMixin,
                                      Dashboards_appTestCase):
    view_name = 'dashboard-list-by-year'

    def get_view_kwargs(self):
        return {'year': now().year}


class MonthDashboardListLanguageFallback(ViewLanguageFallbackMixin,
                                       Dashboards_appTestCase):
    view_name = 'dashboard-list-by-month'

    def get_view_kwargs(self):
        kwargs = {
            'year': now().year,
            'month': now().month,
        }
        return kwargs


class DayDashboardListLanguageFallback(ViewLanguageFallbackMixin,
                                     Dashboards_appTestCase):
    view_name = 'dashboard-list-by-day'

    def get_view_kwargs(self):
        kwargs = {
            'year': now().year,
            'month': now().month,
            'day': now().day,
        }
        return kwargs


# class AuthorDashboardListLanguageFallback(ViewLanguageFallbackMixin,
#                                         Dashboards_appTestCase):
#     view_name = 'dashboard-list-by-author'
#
#     def get_view_kwargs(self):
#         kwargs = {
#             'author': self.author.slug
#         }
#         return kwargs


class CategoryDashboardListLanguageFallback(ViewLanguageFallbackMixin,
                                          Dashboards_appTestCase):
    view_name = 'dashboard-list-by-category'

    def get_view_kwargs(self):
        kwargs = {
            'category': self.category1.slug
        }
        return kwargs


class CategoryFeedListLanguageFallback(ViewLanguageFallbackMixin,
                                       Dashboards_appTestCase):
    view_name = 'dashboard-list-by-category-feed'

    def get_view_kwargs(self):
        kwargs = {
            'category': self.category1.slug
        }
        return kwargs


class TagDashboardListLanguageFallback(ViewLanguageFallbackMixin,
                                     Dashboards_appTestCase):
    view_name = 'dashboard-list-by-tag'

    def get_view_kwargs(self):
        kwargs = {
            'tag': 'tag1'
        }
        return kwargs


class TagFeedLanguageFallback(ViewLanguageFallbackMixin,
                              Dashboards_appTestCase):
    view_name = 'dashboard-list-by-tag-feed'

    def get_view_kwargs(self):
        kwargs = {
            'tag': 'tag1'
        }
        return kwargs
