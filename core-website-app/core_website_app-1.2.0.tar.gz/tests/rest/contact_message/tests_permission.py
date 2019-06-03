""" Authentication tests for contact Message REST API
"""

from django.test import SimpleTestCase
from mock.mock import patch
from rest_framework import status

import core_website_app.rest.contact_message.views as contact_message_views
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_website_app.components.contact_message.models import ContactMessage
from core_website_app.rest.contact_message.serializers import ContactMessageSerializer


class TestContactMessageListGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            contact_message_views.ContactMessageList.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_get(
            contact_message_views.ContactMessageList.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(ContactMessage, "get_all")
    @patch.object(ContactMessageSerializer, "data")
    def test_is_staff_returns_http_200(self,
                                       account_serializer_data,
                                       account_get_all):
        account_get_all.return_value = {}
        account_serializer_data.return_value = True

        response = RequestMock.do_request_get(
            contact_message_views.ContactMessageList.as_view(),
            create_mock_user('1', is_staff=True),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestContactMessageListPostPermission(SimpleTestCase):

    def setUp(self):
        self.mock_account_request = ContactMessage(name="mock",
                                                   content="mock",
                                                   email="mock@mock.com")
        self.mock_data = {
                "name": "name",
                "content": "message",
                "email": "email"
            }

    @patch.object(ContactMessageSerializer, "is_valid")
    @patch.object(ContactMessageSerializer, "save")
    @patch.object(ContactMessageSerializer, "data")
    def test_anonymous_returns_http_201(self,
                                        contact_serializer_data,
                                        contact_serializer_save,
                                        contact_serializer_is_valid):
        response = RequestMock.do_request_post(
            contact_message_views.ContactMessageList.as_view(),
            create_mock_user('1', is_anonymous=True),
            data=self.mock_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch.object(ContactMessageSerializer, "is_valid")
    @patch.object(ContactMessageSerializer, "save")
    @patch.object(ContactMessageSerializer, "data")
    def test_is_authenticated_returns_http_201(self,
                                               contact_serializer_data,
                                               contact_serializer_save,
                                               contact_serializer_is_valid):
        response = RequestMock.do_request_post(
            contact_message_views.ContactMessageList.as_view(),
            create_mock_user('1', is_anonymous=False),
            data=self.mock_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch.object(ContactMessageSerializer, "is_valid")
    @patch.object(ContactMessageSerializer, "save")
    @patch.object(ContactMessageSerializer, "data")
    def test_is_staff_returns_http_201(self,
                                       contact_serializer_data,
                                       contact_serializer_save,
                                       contact_serializer_is_valid):
        response = RequestMock.do_request_post(
            contact_message_views.ContactMessageList.as_view(),
            create_mock_user('1', is_staff=True),
            data=self.mock_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestAContactMessageDetailGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            contact_message_views.ContactMessageDetail.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_get(
            contact_message_views.ContactMessageDetail.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(ContactMessage, "get_by_id")
    @patch.object(ContactMessageSerializer, "data")
    def test_is_staff_returns_http_200(self,
                                       contact_serializer_data,
                                       contact_get_by_id):
        response = RequestMock.do_request_get(
            contact_message_views.ContactMessageDetail.as_view(),
            create_mock_user('1', is_staff=True),
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAContactMessageDetailDeletePermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_delete(
            contact_message_views.ContactMessageDetail.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_delete(
            contact_message_views.ContactMessageDetail.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(ContactMessage, "get_by_id")
    @patch.object(ContactMessageSerializer, "data")
    @patch('core_website_app.components.contact_message.api.delete')
    def test_is_staff_returns_http_200(self,
                                       contact_api,
                                       contact_serializer_data,
                                       contact_get_by_id):
        response = RequestMock.do_request_delete(
            contact_message_views.ContactMessageDetail.as_view(),
            create_mock_user('1', is_staff=True),
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
