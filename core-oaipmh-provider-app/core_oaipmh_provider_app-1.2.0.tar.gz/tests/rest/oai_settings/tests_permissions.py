""" Authentication tests for OAI Settings REST API
"""
from django.test import SimpleTestCase
from mock import Mock
from mock.mock import patch
from rest_framework import status
from rest_framework.status import HTTP_200_OK

from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_oaipmh_provider_app.rest.oai_settings import views as settings_views
from core_oaipmh_provider_app.rest.serializers import SettingsSerializer


class SettingsGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            settings_views.Settings.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            settings_views.Settings.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiSettings, "get")
    @patch.object(SettingsSerializer, "data")
    def test_staff_returns_http_200(self, oai_settings_serializer_data, oai_settings_get):
        oai_settings_serializer_data.return_value = True
        oai_settings_get.return_value = {}
        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            settings_views.Settings.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SettingsPatchPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_patch(
            settings_views.Settings.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_patch(
            settings_views.Settings.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiSettings, "get")
    @patch.object(SettingsSerializer, "is_valid")
    @patch.object(SettingsSerializer, "save")
    @patch.object(SettingsSerializer, "data")
    def test_staff_returns_http_200(self, oai_settings_serializer_data,
                                    oai_settings_serializer_save,
                                    oai_settings_serializer_is_valid,
                                    oai_settings_get):
        oai_settings_serializer_data.return_value = True
        oai_settings_serializer_save.return_value = None
        oai_settings_serializer_is_valid.return_value = {}
        oai_settings_get.return_value = {}
        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_patch(
            settings_views.Settings.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CheckGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            settings_views.Check.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            settings_views.Check.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('requests.get')
    def test_staff_returns_http_200(self, mock_send_get_request):
        mock_send_get_request.return_value = _create_mock_http_request(status_code=HTTP_200_OK)
        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            settings_views.Check.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


def _create_mock_http_request(status_code):
    """ Return a mock HTTP Request

    Args:
        status_code:

    Returns:

    """
    mock_request = Mock()
    mock_request.status_code = status_code
    return mock_request
