""" Unit Test Rest OaiSettings
"""
import requests
from django.test.testcases import SimpleTestCase
from mock.mock import patch
from rest_framework import status

from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.rest.oai_settings import views as  \
    rest_oai_settings
from core_main_app.utils.tests_tools.MockUser import create_mock_user


class TestSelect(SimpleTestCase):
    def setUp(self):
        super(TestSelect, self).setUp()
        self.data = None

    def test_select_unauthorized(self):
        # Arrange
        user = create_mock_user("1", is_staff=False)

        # Act
        response = RequestMock.\
            do_request_get(rest_oai_settings.Settings.as_view(), user, self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCheckRegistry(SimpleTestCase):
    def setUp(self):
        super(TestCheckRegistry, self).setUp()
        self.data = None

    def test_check_registry_unauthorized(self):
        # Arrange
        user = create_mock_user("1", is_staff=False)

        # Act
        response = RequestMock.\
            do_request_get(rest_oai_settings.Check.as_view(), user, self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(requests, 'get')
    def test_check_registry_available(self, mock_get):
        # Arrange
        mock_get.return_value.status_code = status.HTTP_200_OK
        user = create_mock_user("1", is_staff=True)

        # Act
        response = RequestMock.\
            do_request_get(rest_oai_settings.Check.as_view(), user, self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(requests, 'get')
    def test_check_registry_unavailable(self, mock_get):
        # Arrange
        mock_get.return_value.status_code = status.HTTP_404_NOT_FOUND
        user = create_mock_user("1", is_staff=True)

        # Act
        response = RequestMock. \
            do_request_get(rest_oai_settings.Check.as_view(), user, self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUpdate(SimpleTestCase):
    def setUp(self):
        super(TestUpdate, self).setUp()
        self.data = {"repository_name": "value", "repository_identifier": "value",
                     "enable_harvesting": "True"}

    def test_update_unauthorized(self):
        # Act
        response = RequestMock.\
            do_request_patch(rest_oai_settings.Settings.as_view(),
                             user=create_mock_user("1", is_staff=False), data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
