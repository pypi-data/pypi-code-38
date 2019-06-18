import django
from django.conf import settings
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.instrumentation import control
from stackifyapm.contrib.django.client import get_client
from tests.contrib.django.fixtures.testapp.settings import TEST_SETTINGS


class GetClientTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.contrib.django.apps.setup_logging')
        self.setup_logging.start()

        if not settings.configured:
            settings.configure(**TEST_SETTINGS)
            django.setup()

    def tearDown(self):
        control.uninstrument()
        self.setup_logging.stop()

    def test_should_return_client(self):
        client = get_client()

        assert isinstance(client, Client)

    def test_client_config(self):
        client = get_client()

        assert client.config.application_name == 'Python Application'
        assert client.config.environment == 'test'
        assert client.config.config_file == 'stackify.json'
        assert client.config.framework_name == 'django'
        assert client.config.framework_version
