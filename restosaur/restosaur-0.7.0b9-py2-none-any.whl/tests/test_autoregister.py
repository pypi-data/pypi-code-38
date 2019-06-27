import unittest

import django

from django.test import SimpleTestCase, Client


class DjangoAppBasedAutodiscoverTestCase(SimpleTestCase):
    @unittest.skipIf(
            django.VERSION < (1, 7, 0),
            'Not supported for Django %s' % django.get_version())
    def test_successful_autoregistering_root_resource_from_app(self):
        django.setup()

        with self.settings(
                ROOT_URLCONF='tests.urls_autoregister',
                INSTALLED_APPS=['restosaur', 'tests.artest']):
            from .urls_autoregister import api
            self.assertEqual(len(api.resources), 1)
            self.assertEqual(api.resources[0].path, '/')

    @unittest.skipIf(
            django.VERSION < (1, 7, 0),
            'Not supported for Django %s' % django.get_version())
    def test_valid_response_from_autoregistered_app(self):
        c = Client()

        with self.settings(
                ROOT_URLCONF='tests.urls_autoregister',
                INSTALLED_APPS=['restosaur', 'tests.artest']):
            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)

    @unittest.skipIf(
            django.VERSION < (1, 7, 0),
            'Not supported for Django %s' % django.get_version())
    def test_successful_registering_artest_app(self):
        from django.apps import apps
        django.setup()

        with self.settings(
                ROOT_URLCONF='tests.urls_autoregister',
                INSTALLED_APPS=['restosaur', 'tests.artest']):
            self.assertTrue(apps.is_installed('tests.artest'))
