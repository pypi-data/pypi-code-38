"""Integration tests for Result rest api
"""
from django.test.utils import override_settings
from rest_framework import status

import core_explore_federated_search_app.rest.result.views as result_views
from core_main_app.utils.integration_tests.integration_base_test_case import MongoIntegrationBaseTestCase
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from tests.rest.result.fixtures.fixtures import ResultFixtures

fixture_data = ResultFixtures()


class TestGetResultDetail(MongoIntegrationBaseTestCase):
    fixture = fixture_data

    def setUp(self):
        super(TestGetResultDetail, self).setUp()
        self.data = None

    def test_get_raise_validation_error_400_if_parameters_are_invalid(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
        }

        # Act
        response = RequestMock.do_request_get(result_views.ResultDetail.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    def test_get_returns_status_500_if_instance_is_not_available(self):
        # Arrange
        user = create_mock_user('0')
        self.param = {
        }

        self.data = {
            'id': '0',
            'instance_name': fixture_data.data_1.name
        }

        # Act
        response = RequestMock.do_request_get(result_views.ResultDetail.as_view(),
                                              user,
                                              self.data,
                                              self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
