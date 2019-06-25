import json
from django.test import SimpleTestCase, Client
from .utils import response_content_as_text


class URLPatternsTestCase(SimpleTestCase):
    def test_successful_calling_apiroot_without_path_prefix(self):
        c = Client()

        with self.settings(ROOT_URLCONF='tests.urls_root_without_prefix'):
            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)

    def test_valid_response_from_apiroot_without_path_prefix(self):
        c = Client()

        with self.settings(ROOT_URLCONF='tests.urls_root_without_prefix'):
            resp = c.get('/')
            resp_json = json.loads(response_content_as_text(resp))
            self.assertEqual(resp_json['root'], 'ok')

    def test_successful_calling_apiroot_with_path_prefix(self):
        c = Client()

        with self.settings(ROOT_URLCONF='tests.urls_root_with_prefix'):
            resp = c.get('/api/')
            self.assertEqual(resp.status_code, 200)

    def test_that_api_trailing_prefix_does_not_affect_urlresolver(self):
        c = Client()

        with self.settings(ROOT_URLCONF='tests.urls_root_with_trailing_slash'):
            resp = c.get('/api/')
            self.assertEqual(resp.status_code, 200)
