"""Integration tests for exporter rest api
"""
from bson import ObjectId
from rest_framework import status

import core_exporters_app.rest.exporters.views as exporter_views
from core_main_app.utils.integration_tests.integration_base_test_case import MongoIntegrationBaseTestCase
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from tests.rest.exporter.fixtures.fixtures import ExporterFixtures

fixture_data = ExporterFixtures()


class TestGetExportersList(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def setUp(self):
        super(TestGetExportersList, self).setUp()

    def test_get_all_returns_status_200_with_no_permission_needed(self):
        # Arrange
        user = create_mock_user('1')

        # Act
        response = RequestMock.do_request_get(exporter_views.ExporterList.as_view(),
                                              user)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetExportersDetail(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def setUp(self):
        super(TestGetExportersDetail, self).setUp()
        self.data = None

    def test_get_returns_object_when_found(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
            'pk': self.fixture.data_1.id
        }

        # Act
        response = RequestMock.do_request_get(exporter_views.ExporterDetail.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_raise_404_when_not_found(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
            'pk': str(ObjectId())
        }

        # Act
        response = RequestMock.do_request_get(exporter_views.ExporterDetail.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_raise_500_sever_error_when_general_error_occured(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
            'pk': '0'
        }

        # Act
        response = RequestMock.do_request_get(exporter_views.ExporterDetail.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestGetExporterDownload(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def setUp(self):
        super(TestGetExporterDownload, self).setUp()
        self.data = None

    def test_get_raise_404_when_not_found(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
            'pk': str(ObjectId())
        }

        # Act
        response = RequestMock.do_request_get(exporter_views.ExporterDownload.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_raise_500_sever_error_when_general_error_occured(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
            'pk': '0'
        }

        # Act
        response = RequestMock.do_request_get(exporter_views.ExporterDownload.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)