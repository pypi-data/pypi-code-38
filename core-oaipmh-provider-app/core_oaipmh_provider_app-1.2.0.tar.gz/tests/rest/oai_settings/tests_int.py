""" Int Test Rest OaiSettings
"""
from rest_framework import status

from core_main_app.utils.integration_tests.integration_base_test_case import \
    MongoIntegrationBaseTestCase
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_oaipmh_provider_app.rest.oai_settings import views as rest_oai_settings
from tests.utils.fixtures.fixtures import OaiPmhFixtures


class TestSelect(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestSelect, self).setUp()
        self.data = None

    def test_select_returns(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_get(rest_oai_settings.Settings.as_view(), user=user,
                                              data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUpdateSettings(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestUpdateSettings, self).setUp()
        self.new_repository_name = "{0}_new".format(self.fixture.settings.repository_name)
        self.new_repository_identifier = "{0}_new".format(self.fixture.settings.
                                                          repository_identifier)
        self.new_enable_harvesting = "True" if (not self.fixture.settings.
                                                enable_harvesting)is True else "False"
        self.data = {"repository_name": str(self.new_repository_name),
                     "repository_identifier": self.new_repository_identifier,
                     "enable_harvesting": str(self.new_enable_harvesting)}

    def test_update(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_patch(rest_oai_settings.Settings.as_view(), user,
                                                self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings_ = OaiSettings.objects.get()
        self.assertEqual(settings_.repository_name, self.new_repository_name)
        self.assertEqual(settings_.repository_identifier, self.new_repository_identifier)
        self.assertEqual(str(settings_.enable_harvesting), self.new_enable_harvesting)
