import json
import webtest
from pyramid.response import Response
from pyramid import testing
from pyramid.view import view_config
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.contrib.pyramid import make_client
from stackifyapm.instrumentation import control


class RegistryMock(object):
    settings = {}

    def __init__(self, name=None, env=None, config_file=None):
        self.settings['APPLICATION_NAME'] = name
        self.settings['ENVIRONMENT'] = env
        self.settings['CONFIG_FILE'] = config_file


class MakeClientTest(TestCase):

    def test_should_return_client(self):
        registry = RegistryMock()
        client = make_client(registry, **registry.settings)

        assert isinstance(client, Client)

    def test_client_default_config(self):
        registry = RegistryMock()
        client = make_client(registry)

        assert client.config.application_name == 'Python Application'
        assert client.config.environment == 'Production'
        assert client.config.config_file == 'stackify.json'
        assert client.config.framework_name == 'pyramid'
        assert client.config.framework_version

    def test_client_config(self):
        registry = RegistryMock(name='MyApp', env='Prod', config_file='somewhere/stackify.json')
        client = make_client(registry)

        assert client.config.application_name == 'MyApp'
        assert client.config.environment == 'Prod'
        assert client.config.config_file == 'somewhere/stackify.json'
        assert client.config.framework_name == 'pyramid'
        assert client.config.framework_version


@view_config(renderer='json')
def index(request):
    return Response(json.dumps({'status': 'OK!'}))


@view_config(renderer='json')
def exception(request):
    5 / 0
    return Response(json.dumps({'status': 'OK!'}))


class StackifyPyramidClientTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.contrib.pyramid.setup_logging')
        self.setup_logging.start()

        config = testing.setUp(settings={
            'application_name': 'MyApplication',
            'environment': 'Test',
        })
        config.add_route('hello', '/')
        config.add_route('exception', '/exception')
        config.add_view(index, route_name='hello')
        config.add_view(exception, route_name='exception')
        config.include('stackifyapm.contrib.pyramid')
        self.app = webtest.TestApp(config.make_wsgi_app())

    def tearDown(self):
        testing.tearDown()
        control.uninstrument()
        self.setup_logging.stop()

    def test_begin_transaction(self):
        begin_transaction = mock.patch('stackifyapm.base.Client.begin_transaction')
        mock_begin_transaction = begin_transaction.start()

        self.app.get('/')

        assert mock_begin_transaction.called
        assert mock_begin_transaction.call_args_list[0][0][0] == 'request'

        begin_transaction.stop()

    def test_end_transaction(self):
        end_transaction = mock.patch('stackifyapm.base.Client.end_transaction')
        mock_end_transaction = end_transaction.start()

        self.app.get('/')

        assert mock_end_transaction.called

        end_transaction.stop()

    def test_capture_exception(self):
        capture_exception = mock.patch('stackifyapm.base.Client.capture_exception')
        end_transaction = mock.patch('stackifyapm.base.Client.end_transaction')
        mock_capture_exception = capture_exception.start()
        end_transaction.start()

        with self.assertRaises(ZeroDivisionError):
            self.app.get('/exception')

        assert mock_capture_exception.called
        assert mock_capture_exception.call_args_list[0][1]['exception']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Frames']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Timestamp']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Exception']
        assert mock_capture_exception.call_args_list[0][1]['exception']['CaughtBy']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Message']

        capture_exception.stop()
        end_transaction.stop()


class StackifyapmHeaderTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.contrib.pyramid.setup_logging')
        self.setup_logging.start()

        self.config = testing.setUp(settings={
            'application_name': 'MyApplication',
            'environment': 'Test',
        })
        self.config.add_route('hello', '/')
        self.config.add_route('exception', '/exception')
        self.config.add_view(index, route_name='hello')
        self.config.add_view(exception, route_name='exception')
        self.config.include('stackifyapm.contrib.pyramid')

    def tearDown(self):
        testing.tearDown()
        control.uninstrument()
        self.setup_logging.stop()

    def test_response_should_contain_stackify_header(self):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert 'X-StackifyID' in res.headers.keys()

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_not_include_client_and_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "C" not in res.headers.get('X-StackifyID')
        assert "CD" not in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_contain_client_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"clientId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" not in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_contain_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "Csome_id" not in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_contain_client_and_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "some_id", "clientId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_get_client_property_call(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "some_id", "clientId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        # do multiple requests
        self.app.get('/')
        self.app.get('/')
        res = self.app.get('/')

        assert get_property_info_mock.call_count == 1
        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_get_client_property_call_fallback(self, get_property_info_mock):
        get_property_info_mock.side_effect = [
            {},  # first get_properties call making sure property is empty
            {"deviceId": "some_id", "clientId": "some_id"},  # second get_properties call
        ]
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        # do multiple requests
        self.app.get('/')
        self.app.get('/')
        res = self.app.get('/')

        assert get_property_info_mock.call_count == 2
        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')
