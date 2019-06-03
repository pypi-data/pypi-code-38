""" Authentication tests for Account Request REST API
"""

from django.test import SimpleTestCase
from mock.mock import patch
from rest_framework import status

import core_website_app.rest.account_request.views as account_request_views
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_website_app.components.account_request.models import AccountRequest
from core_website_app.rest.account_request.serializers import AccountRequestSerializer, UserSerializer


class TestAccountRequestListGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            account_request_views.AccountRequestList.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_get(
            account_request_views.AccountRequestList.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(AccountRequest, "get_all")
    @patch.object(AccountRequestSerializer, "data")
    def test_is_staff_returns_http_200(self,
                                       account_serializer_data,
                                       account_get_all):
        response = RequestMock.do_request_get(
            account_request_views.AccountRequestList.as_view(),
            create_mock_user('1', is_staff=True),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAccountRequestListPostPermission(SimpleTestCase):

    def setUp(self):
        self.mock_data = {
                "username": "username",
                "first_name": "first_name",
                "last_name": "last_name",
                "password": "password",
                "email": "email"
            }

    @patch.object(UserSerializer, "is_valid")
    @patch.object(UserSerializer, "save")
    def test_anonymous_returns_http_201(self,
                                        user_serializer_save,
                                        user_serializer_is_valid):
        response = RequestMock.do_request_post(
            account_request_views.AccountRequestList.as_view(),
            create_mock_user('1', is_anonymous=True),
            data=self.mock_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch.object(UserSerializer, "is_valid")
    @patch.object(UserSerializer, "save")
    def test_is_authenticated_returns_http_201(self,
                                               user_serializer_save,
                                               user_serializer_is_valid):
        response = RequestMock.do_request_post(
            account_request_views.AccountRequestList.as_view(),
            create_mock_user('1', is_anonymous=False),
            data=self.mock_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch.object(UserSerializer, "is_valid")
    @patch.object(UserSerializer, "save")
    def test_is_staff_returns_http_201(self,
                                       user_serializer_save,
                                       user_serializer_is_valid):
        response = RequestMock.do_request_post(
            account_request_views.AccountRequestList.as_view(),
            create_mock_user('1', is_staff=True),
            data=self.mock_data
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestAccountRequestDetailGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            account_request_views.AccountRequestDetail.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_get(
            account_request_views.AccountRequestDetail.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(AccountRequest, "get_by_id")
    @patch.object(AccountRequestSerializer, "data")
    def test_is_staff_returns_http_200(self,
                                       account_serializer_data,
                                       account_get_by_id):
        response = RequestMock.do_request_get(
            account_request_views.AccountRequestDetail.as_view(),
            create_mock_user('1', is_staff=True),
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAccountRequestDenyGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_patch(
            account_request_views.AccountRequestDeny.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_patch(
            account_request_views.AccountRequestDeny.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(AccountRequest, "get_by_id")
    @patch('core_website_app.components.account_request.api.deny')
    def test_is_staff_returns_http_200(self,
                                       account_api,
                                       account_get_by_id):
        response = RequestMock.do_request_patch(
            account_request_views.AccountRequestDeny.as_view(),
            create_mock_user('1', is_staff=True),
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAccountRequestAcceptGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_patch(
            account_request_views.AccountRequestAccept.as_view(),
            create_mock_user('1', is_anonymous=True),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_is_authenticated_returns_http_403(self):
        response = RequestMock.do_request_patch(
            account_request_views.AccountRequestAccept.as_view(),
            create_mock_user('1', is_anonymous=False),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(AccountRequest, "get_by_id")
    @patch('core_website_app.components.account_request.api.accept')
    def test_is_staff_returns_http_200(self,
                                       account_api,
                                       account_get_by_id):
        response = RequestMock.do_request_patch(
            account_request_views.AccountRequestAccept.as_view(),
            create_mock_user('1', is_staff=True),
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)