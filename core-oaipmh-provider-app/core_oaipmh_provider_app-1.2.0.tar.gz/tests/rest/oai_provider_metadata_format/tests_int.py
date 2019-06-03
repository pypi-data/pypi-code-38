""" Int Test Rest OaiProviderMetadataFormat
"""
import requests
from mock.mock import patch
from rest_framework import status

from core_main_app.utils.integration_tests.integration_base_test_case import \
    MongoIntegrationBaseTestCase
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import  \
    OaiProviderMetadataFormat
from core_oaipmh_provider_app.rest.oai_provider_metadata_format import views as \
    rest_oai_provider_metadata_format
from tests.utils.fixtures.fixtures import OaiPmhFixtures, OaiPmhMock


class TestSelectMetadataFormat(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestSelectMetadataFormat, self).setUp()
        self.param = {"metadata_format_id": str(OaiPmhMock().mock_oai_first_metadata_format().id)}

    def test_select_metadata_format_returns(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_get(rest_oai_provider_metadata_format.
                                              MetadataFormatDetail.as_view(), user=user, param=self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestSelectAllMetadataFormats(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestSelectAllMetadataFormats, self).setUp()
        self.data = None

    def test_select_all_metadata_formats(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_get(rest_oai_provider_metadata_format.
                                              MetadataFormatsList.as_view(), user, self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestAddMetadataFormat(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestAddMetadataFormat, self).setUp()
        self.data = {"metadata_prefix": "oai_test", "schema_url": "http://www.dummy.org"}
        self.nb_metadata_formats = len(OaiProviderMetadataFormat.objects.all())

    @patch.object(requests, 'get')
    def test_add_metadata_format(self, mock_get):
        # Arrange
        text = "<schema xmlns='http://www.w3.org/2001/XMLSchema'></schema>"
        mock_get.return_value.status_code = status.HTTP_200_OK
        mock_get.return_value.text = text
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_post(rest_oai_provider_metadata_format.
                                               MetadataFormatsList.as_view(), user, self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(OaiProviderMetadataFormat.objects.all()), self.nb_metadata_formats + 1)


class TestAddTemplateMetadataFormat(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestAddTemplateMetadataFormat, self).setUp()
        self.data = {"metadata_prefix": "oai_test", "template_id": str(
            OaiPmhMock.mock_oai_first_template().id)}
        self.nb_template_metadata_formats = len(OaiProviderMetadataFormat.objects.all())

    def test_add_template_metadata_format(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_post(rest_oai_provider_metadata_format.
                                               TemplateAsMetadataFormat.as_view(), user,
                                               self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(OaiProviderMetadataFormat.objects.all()),
                         self.nb_template_metadata_formats + 1)


class TestDeleteMetadataFormat(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestDeleteMetadataFormat, self).setUp()
        self.param = {"metadata_format_id": str(OaiPmhMock().mock_oai_first_metadata_format().id)}
        self.nb_metadata_formats = len(OaiProviderMetadataFormat.objects.all())

    def test_delete_metadata_format(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_delete(rest_oai_provider_metadata_format.
                                                 MetadataFormatDetail.as_view(), user, param=self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(OaiProviderMetadataFormat.objects.all()), self.nb_metadata_formats - 1)


class TestUpdateMetadataFormat(MongoIntegrationBaseTestCase):
    fixture = OaiPmhFixtures()

    def setUp(self):
        super(TestUpdateMetadataFormat, self).setUp()
        self.first_metadata_format = OaiPmhMock.mock_oai_first_metadata_format()
        self.new_metadata_prefix = "{0}_new".format(self.first_metadata_format.metadata_prefix)
        self.param = {"metadata_format_id": str(self.first_metadata_format.id)}
        self.data = {"metadata_prefix": self.new_metadata_prefix}

    def test_update_metadata_format(self):
        # Arrange
        user = create_mock_user('1', is_staff=True)

        # Act
        response = RequestMock.do_request_patch(rest_oai_provider_metadata_format.
                                                MetadataFormatDetail.as_view(), user, data=self.data,
                                                param=self.param)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(OaiProviderMetadataFormat.objects.
                         get(pk=self.first_metadata_format.id).metadata_prefix,
                         self.new_metadata_prefix)
