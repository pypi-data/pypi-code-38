""" Authentication tests for Type Version Manager REST API
"""
from django.test import SimpleTestCase
from mock.mock import patch
from rest_framework import status

from core_composer_app.components.type_version_manager.models import TypeVersionManager
from core_composer_app.rest.type_version_manager import views as type_version_manager_views
from core_composer_app.rest.type_version_manager.serializers import TypeVersionManagerSerializer, \
    CreateTypeSerializer
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock


class TestGlobalTypeVersionManagerListGetPermission(SimpleTestCase):

    @patch.object(TypeVersionManager, "get_global_version_managers")
    def test_anonymous_returns_http_200(self, type_version_manager_get_all_global_version_managers):
        type_version_manager_get_all_global_version_managers.return_value = {}

        response = RequestMock.do_request_get(
            type_version_manager_views.GlobalTypeVersionManagerList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(TypeVersionManager, "get_global_version_managers")
    def test_authenticated_returns_http_200(self, type_version_manager_get_all_global_version_managers):
        type_version_manager_get_all_global_version_managers.return_value = {}

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            type_version_manager_views.GlobalTypeVersionManagerList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(TypeVersionManager, "get_global_version_managers")
    def test_staff_returns_http_200(self, type_version_manager_get_all_global_version_managers):
        type_version_manager_get_all_global_version_managers.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            type_version_manager_views.GlobalTypeVersionManagerList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserTypeVersionManagerListGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            type_version_manager_views.UserTypeVersionManagerList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(TypeVersionManager, "get_version_managers_by_user")
    def test_authenticated_returns_http_200(self, type_version_manager_get_version_managers_by_user):
        type_version_manager_get_version_managers_by_user.return_value = {}

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            type_version_manager_views.UserTypeVersionManagerList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(TypeVersionManager, "get_version_managers_by_user")
    def test_staff_returns_http_200(self, type_version_manager_get_version_managers_by_user):
        type_version_manager_get_version_managers_by_user.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            type_version_manager_views.UserTypeVersionManagerList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserTypeListPostPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            type_version_manager_views.UserTypeList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(CreateTypeSerializer, "is_valid")
    @patch.object(CreateTypeSerializer, "save")
    @patch.object(CreateTypeSerializer, "data")
    @patch.object(TypeVersionManagerSerializer, "is_valid")
    @patch.object(TypeVersionManagerSerializer, "save")
    @patch.object(TypeVersionManagerSerializer, "data")
    def test_authenticated_returns_http_201(self, type_version_manager_serializer_data,
                                            type_version_manager_serializer_save,
                                            type_version_manager_serializer_valid,
                                            create_type_version_manager_serializer_data,
                                            create_type_version_manager_serializer_save,
                                            create_type_version_manager_serializer_valid):
        create_type_version_manager_serializer_data.return_value = True
        create_type_version_manager_serializer_save.return_value = None
        create_type_version_manager_serializer_valid.return_value = {}
        type_version_manager_serializer_data.return_value = True
        type_version_manager_serializer_save.return_value = None
        type_version_manager_serializer_valid.return_value = {}

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_post(
            type_version_manager_views.UserTypeList.as_view(),
            mock_user,
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch.object(CreateTypeSerializer, "is_valid")
    @patch.object(CreateTypeSerializer, "save")
    @patch.object(CreateTypeSerializer, "data")
    @patch.object(TypeVersionManagerSerializer, "is_valid")
    @patch.object(TypeVersionManagerSerializer, "save")
    @patch.object(TypeVersionManagerSerializer, "data")
    def test_staff_returns_http_201(self, type_version_manager_serializer_data,
                                    type_version_manager_serializer_save,
                                    type_version_manager_serializer_valid,
                                    create_type_version_manager_serializer_data,
                                    create_type_version_manager_serializer_save,
                                    create_type_version_manager_serializer_valid):
        create_type_version_manager_serializer_data.return_value = True
        create_type_version_manager_serializer_save.return_value = None
        create_type_version_manager_serializer_valid.return_value = {}
        type_version_manager_serializer_data.return_value = True
        type_version_manager_serializer_save.return_value = None
        type_version_manager_serializer_valid.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_post(
            type_version_manager_views.UserTypeList.as_view(),
            mock_user,
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestGlobalTypeListPostPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            type_version_manager_views.GlobalTypeList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_post(
            type_version_manager_views.GlobalTypeList.as_view(),
            mock_user,
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(CreateTypeSerializer, "is_valid")
    @patch.object(CreateTypeSerializer, "save")
    @patch.object(CreateTypeSerializer, "data")
    @patch.object(TypeVersionManagerSerializer, "is_valid")
    @patch.object(TypeVersionManagerSerializer, "save")
    @patch.object(TypeVersionManagerSerializer, "data")
    def test_staff_returns_http_201(self, type_version_manager_serializer_data,
                                    type_version_manager_serializer_save,
                                    type_version_manager_serializer_valid,
                                    create_type_version_manager_serializer_data,
                                    create_type_version_manager_serializer_save,
                                    create_type_version_manager_serializer_valid):
        create_type_version_manager_serializer_data.return_value = True
        create_type_version_manager_serializer_save.return_value = None
        create_type_version_manager_serializer_valid.return_value = {}
        type_version_manager_serializer_data.return_value = True
        type_version_manager_serializer_save.return_value = None
        type_version_manager_serializer_valid.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_post(
            type_version_manager_views.GlobalTypeList.as_view(),
            mock_user,
            data={}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

