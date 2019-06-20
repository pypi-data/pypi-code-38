# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import activate, override

from dashboards_app.models import Dashboard
from cms import api

from . import Dashboards_appTestCase, Dashboards_appTransactionTestCase, TESTS_STATIC_ROOT

FEATURED_IMAGE_PATH = os.path.join(TESTS_STATIC_ROOT, 'featured_image.jpg')


class TestModels(Dashboards_appTestCase):

    def test_create_dashboard(self):
        dashboard = self.create_dashboard()
        response = self.client.get(dashboard.get_absolute_url())
        self.assertContains(response, dashboard.title)

    def test_delete_dashboard(self):
        dashboard = self.create_dashboard()
        dashboard_pk = dashboard.pk
        dashboard_url = dashboard.get_absolute_url()
        response = self.client.get(dashboard_url)
        self.assertContains(response, dashboard.title)
        Dashboard.objects.get(pk=dashboard_pk).delete()
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 404)

    def test_auto_slugifies(self):
        activate(self.language)
        title = u'This is a title'
        author = self.create_person()
        dashboard = Dashboard.objects.create(
            title=title, author=author, owner=author.user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        dashboard.save()
        self.assertEquals(dashboard.slug, 'this-is-a-title')
        # Now, let's try another with the same title
        dashboard_1 = Dashboard(
            title=title.lower(),
            author=author,
            owner=author.user,
            app_config=self.app_config,
            publishing_date=now(),
            is_published=True,
        )
        # Note, it cannot be the exact same title, else we'll fail the unique
        # constraint on the field.
        dashboard_1.save()
        # Note that this should be "incremented" slug here.
        self.assertEquals(dashboard_1.slug, 'this-is-a-title-1')
        dashboard_2 = Dashboard(
            title=title.upper(),
            author=author,
            owner=author.user,
            app_config=self.app_config,
            publishing_date=now(),
            is_published=True,
        )
        dashboard_2.save()
        self.assertEquals(dashboard_2.slug, 'this-is-a-title-2')

    def test_auto_existing_author(self):
        author = self.create_person()
        dashboard = Dashboard.objects.create(
            title=self.rand_str(), owner=author.user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        dashboard.save()
        self.assertEquals(dashboard.author.user, dashboard.owner)

        old = self.app_config.create_authors
        self.app_config.create_authors = False
        self.app_config.save()
        dashboard = Dashboard.objects.create(
            title=self.rand_str(), owner=author.user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        self.app_config.create_authors = old
        self.app_config.save()
        self.assertEquals(dashboard.author, None)

    def test_auto_new_author(self):
        user = self.create_user()
        dashboard = Dashboard.objects.create(
            title=self.rand_str(), owner=user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        dashboard.save()
        self.assertEquals(dashboard.author.name,
                          u' '.join((user.first_name, user.last_name)))

    def test_auto_search_data(self):
        activate(self.language)

        user = self.create_user()

        lead_in = 'Hello! this text will be searchable.'

        Dashboard.update_search_on_save = True

        dashboard = Dashboard.objects.create(
            title=self.rand_str(),
            owner=user,
            lead_in=lead_in,
            app_config=self.app_config,
            publishing_date=now(),
            is_published=True,
        )
        dashboard.save()

        search_data = dashboard.get_search_data()

        self.assertEquals(lead_in, search_data)
        self.assertEquals(dashboard.search_data, search_data)

    def test_auto_search_data_off(self):
        activate(self.language)
        user = self.create_user()

        lead_in = 'Hello! this text will not be searchable.'

        Dashboard.update_search_on_save = False

        dashboard = Dashboard.objects.create(
            title=self.rand_str(),
            owner=user,
            lead_in=lead_in,
            app_config=self.app_config,
            publishing_date=now(),
            is_published=True,
        )
        dashboard.save()

        search_data = dashboard.get_search_data()

        # set it back to true
        Dashboard.update_search_on_save = True

        self.assertEquals(lead_in, search_data)
        self.assertNotEquals(dashboard.search_data, search_data)

    def test_has_content(self):
        # Just make sure we have a known language
        activate(self.language)
        title = self.rand_str()
        content = self.rand_str()
        author = self.create_person()
        dashboard = Dashboard.objects.create(
            title=title, slug=self.rand_str(), author=author, owner=author.user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        dashboard.save()
        api.add_plugin(dashboard.content, 'TextPlugin', self.language)
        plugin = dashboard.content.get_plugins()[0].get_plugin_instance()[0]
        plugin.body = content
        plugin.save()
        response = self.client.get(dashboard.get_absolute_url())
        self.assertContains(response, title)
        self.assertContains(response, content)

    def test_change_title(self):
        """
        Test that we can change the title of an existing, published dashboard
        without issue. Also ensure that the slug does NOT change when changing
        the title alone.
        """
        activate(self.language)
        initial_title = "This is the initial title"
        initial_slug = "this-is-the-initial-title"
        author = self.create_person()
        dashboard = Dashboard.objects.create(
            title=initial_title, author=author, owner=author.user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        dashboard.save()
        self.assertEquals(dashboard.title, initial_title)
        self.assertEquals(dashboard.slug, initial_slug)
        # Now, let's try to change the title
        new_title = "This is the new title"
        dashboard.title = new_title
        dashboard.save()
        dashboard = self.reload(dashboard)
        self.assertEquals(dashboard.title, new_title)
        self.assertEquals(dashboard.slug, initial_slug)


class TestModelsTransactions(Dashboards_appTransactionTestCase):

    def test_duplicate_title_and_language(self):
        """
        Test that if user attempts to create an dashboard with the same name and
        in the same language as another, it will not raise exceptions.
        """
        title = "Sample Dashboard"
        author = self.create_person()
        original_lang = settings.LANGUAGES[0][0]
        # Create an initial dashboard in the first language
        dashboard1 = Dashboard(
            title=title, author=author, owner=author.user,
            app_config=self.app_config, publishing_date=now(),
            is_published=True,
        )
        dashboard1.set_current_language(original_lang)
        dashboard1.save()

        # Now try to create an dashboard with the same title in every possible
        # language and every possible language contexts.
        for context_lang, _ in settings.LANGUAGES:
            with override(context_lang):
                for dashboard_lang, _ in settings.LANGUAGES:
                    try:
                        dashboard = Dashboard(
                            author=author, owner=author.user,
                            app_config=self.app_config, publishing_date=now(),
                            is_published=True,
                        )
                        dashboard.set_current_language(dashboard_lang)
                        dashboard.title = title
                        dashboard.save()
                    except Exception:
                        self.fail('Creating dashboard in process context "{0}" '
                            'and dashboard language "{1}" with identical name '
                            'as another "{2}" dashboard raises exception'.format(
                                context_lang,
                                dashboard_lang,
                                original_lang,
                            ))
