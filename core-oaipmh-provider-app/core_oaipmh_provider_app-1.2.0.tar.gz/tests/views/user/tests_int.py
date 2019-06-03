""" Integrations tests for user views
"""
from mock import PropertyMock
from mock.mock import patch
from rest_framework import status

from core_main_app.components.data.models import Data
from core_main_app.utils.integration_tests.integration_base_test_case import \
    MongoIntegrationBaseTestCase
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.components.oai_provider_metadata_format import api as \
    oai_provider_metadata_format_api
from core_oaipmh_provider_app.views.user.views import OAIProviderView
from tests.utils.fixtures.fixtures import OaiPmhFixtures
from tests.utils.test_oai_pmh_suite import TestOaiPmhSuite

fixture_data = OaiPmhFixtures()


class TestVerbs(TestOaiPmhSuite, MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def test_identify(self):
        # Arrange
        data = {'verb': 'Identify'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'Identify')

    @patch.object(Data, "xml_content", new_callable=PropertyMock)
    def test_get_record(self, mock_xml_content):
        # Arrange
        mock_xml_content.return_value = "<tag>value</tag>"
        data = {'verb': 'GetRecord', 'metadataPrefix': "oai_demo",
                'identifier': self.fixture.data_identifiers[0]}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'record')

    def test_get_list_identifiers(self):
        # Arrange
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': "oai_demo"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListIdentifiers')
        self.check_tag_count(response.rendered_content, 'identifier', self.fixture.nb_public_data)

    @patch.object(Data, "xml_content", new_callable=PropertyMock)
    def test_get_list_records(self, mock_xml_content):
        # Arrange
        mock_xml_content.return_value = "<tag>value</tag>"
        data = {'verb': 'ListRecords', 'metadataPrefix': "oai_demo"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListRecords')
        self.check_tag_count(response.rendered_content, 'record', self.fixture.nb_public_data)

    @patch.object(oai_provider_metadata_format_api, 'get_metadata_format_schema_url')
    def test_get_list_metadata_formats(self, mock_get_metadata_format_schema_url):
        # Arrange
        data = {'verb': 'ListMetadataFormats'}
        mock_get_metadata_format_schema_url.return_value = "dummy_schema"

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListMetadataFormats')
        self.check_tag_count(response.rendered_content, 'metadataFormat',
                             len(self.fixture.oai_metadata_formats))

    @patch.object(oai_provider_metadata_format_api, 'get_metadata_format_schema_url')
    def test_get_list_metadata_formats_with_identifier(self, mock_get_metadata_format_schema_url):
        # Arrange
        data = {'verb': 'ListMetadataFormats', 'identifier': self.fixture.data_identifiers[0]}
        mock_get_metadata_format_schema_url.return_value = "dummy_schema"

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListMetadataFormats')

    def test_get_list_sets(self):
        # Arrange
        data = {'verb': 'ListSets'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), user=_create_user('1'),
                                              data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListSets')
        self.check_tag_count(response.rendered_content, 'set', len(self.fixture.oai_sets))


def _create_user(user_id, is_superuser=False):
    return create_mock_user(user_id, is_superuser=is_superuser)
