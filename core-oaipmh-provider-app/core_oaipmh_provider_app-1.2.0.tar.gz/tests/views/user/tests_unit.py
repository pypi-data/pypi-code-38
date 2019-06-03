""" Unit Test Rest OaiRegistry
"""
from datetime import datetime

from bson.objectid import ObjectId
from django.http.request import HttpRequest
from mock.mock import patch, Mock
from rest_framework import status
from rest_framework.status import HTTP_200_OK


import core_main_app.components.xsl_transformation.api as xsl_transformation_api

from core_main_app.commons import exceptions as common_exceptions
from core_main_app.components.data import api as data_api
from core_main_app.components.template.models import Template
from core_main_app.components.xsl_transformation.models import XslTransformation
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.commons import exceptions, status as oai_status
from core_oaipmh_provider_app.components.oai_data import api as oai_data_api
from core_oaipmh_provider_app.components.oai_data.models import OaiData
from core_oaipmh_provider_app.components.oai_provider_metadata_format import \
    api as oai_provider_metadata_format_api
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import \
    OaiProviderMetadataFormat
from core_oaipmh_provider_app.components.oai_provider_set import api as oai_provider_set_api
from core_oaipmh_provider_app.components.oai_provider_set.models import OaiProviderSet
from core_oaipmh_provider_app.components.oai_settings import api as oai_settings_api
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_oaipmh_provider_app.components.oai_xsl_template import api as oai_xsl_template_api
from core_oaipmh_provider_app.components.oai_xsl_template.models import OaiXslTemplate
from core_oaipmh_provider_app.utils import CheckOaiPmhRequest
from core_oaipmh_provider_app.views.user.views import OAIProviderView
from tests.utils.test_oai_pmh_suite import TestOaiPmhSuite


class TestServerGeneral(TestOaiPmhSuite):
    def setUp(self):
        super(TestServerGeneral, self).setUp()
        self.data = {}

    def test_no_setting(self):
        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch.object(oai_settings_api, 'get')
    def test_no_harvesting(self, mock_get):
        # Arrange
        mock_get.return_value.enable_harvesting = False

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=self.data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch.object(oai_settings_api, 'get')
    @patch.object(HttpRequest, 'build_absolute_uri')
    def test_no_verb(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value.enable_harvesting = True
        mock_request.return_value = ""

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=self.data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadVerb))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_VERB)

    @patch.object(oai_settings_api, 'get')
    @patch.object(HttpRequest, 'build_absolute_uri')
    def test_bad_verb(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value.enable_harvesting = True
        mock_request.return_value = ""
        bad_verb = {'verb': 'dummy'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_verb)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadVerb))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_VERB)


class TestIdentify(TestOaiPmhSuite):
    @patch.object(oai_settings_api, 'get')
    @patch.object(HttpRequest, 'build_absolute_uri')
    def test_illegal_argument(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value.enable_harvesting = True
        mock_request.return_value = ""
        bad_arg = {'verb': 'Identify', 'test': 'test'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)


class TestListSets(TestOaiPmhSuite):
    @patch.object(oai_settings_api, 'get')
    @patch.object(HttpRequest, 'build_absolute_uri')
    def test_duplicate_argument(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value.enable_harvesting = True
        mock_request.return_value = ""
        bad_arg = {'verb': ['ListSets', 'ListSets']}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_identify(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        data = {'verb': 'Identify'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'Identify')

    @patch.object(oai_provider_set_api, 'get_all')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_sets_no_sets(self, mock_get, mock_request, mock_get_all):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_get_all.return_value = []
        mock_request.return_value = ""
        data = {'verb': 'ListSets'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_error_code(response.rendered_content, exceptions.NO_SET_HIERARCHY)

    @patch.object(oai_provider_set_api, 'get_all')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_sets(self, mock_get, mock_request, mock_get_all):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        list_oai_sets = [_create_mock_oai_sets(), _create_mock_oai_sets()]
        mock_get_all.return_value = list_oai_sets
        mock_request.return_value = ""
        data = {'verb': 'ListSets'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content,'ListSets')
        self.check_tag_count(response.rendered_content, 'set', len(list_oai_sets))


class TestListIdentifiers(TestOaiPmhSuite):
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_identifiers_error_metadata_prefix_missing(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        bad_arg = {'verb': ['ListIdentifiers']}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_identifiers_error_date_until(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        bad_arg = {'verb': 'ListIdentifiers', 'metadataPrefix': 'dummy', 'from': 'bad_date'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_identifiers_error_date_from(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        bad_arg = {'verb': 'ListIdentifiers', 'metadataPrefix': 'dummy', 'until': 'bad_date'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_identifiers_no_metadata_format(self, mock_get, mock_request, mock_get_by_metadata_prefix):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_by_metadata_prefix.side_effect = common_exceptions.DoesNotExist('')
        bad_arg = {'verb': 'ListIdentifiers', 'metadataPrefix': 'dummy'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.CannotDisseminateFormat))
        self.check_tag_error_code(response.rendered_content, exceptions.DISSEMINATE_FORMAT)

    @patch.object(oai_provider_set_api, 'get_by_set_spec')
    @patch.object(oai_xsl_template_api, 'get_template_ids_by_metadata_format')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(OAIProviderView, '_get_templates_id_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_identifiers_no_set_or_bad_set(self, mock_get, mock_request, mock_get_templates_id,
                                                mock_get_by_metadata_prefix, mock_get_template_ids,
                                                mock_get_by_set_spec):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_templates_id.return_value = []
        mock_get_by_metadata_prefix.return_value = []
        mock_get_template_ids.return_value = [ObjectId()]
        mock_get_by_set_spec.side_effect = common_exceptions.DoesNotExist('')
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'dummy', 'set': 'dummy_set'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.NoRecordsMatch))
        self.check_tag_error_code(response.rendered_content, exceptions.NO_RECORDS_MATCH)

    @patch.object(oai_data_api, 'get_all_by_template')
    @patch.object(OAIProviderView, '_get_templates_id_by_set_spec')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(OAIProviderView, '_get_templates_id_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_identifiers_no_xml_data(self, mock_get, mock_request, mock_get_templates_id,
                                          mock_get_by_metadata_prefix, mock_get_templates_id_by_set_spec,
                                          mock_get_all_by_template):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_templates_id.return_value = [ObjectId()]
        mock_get_by_metadata_prefix.return_value = []
        mock_get_templates_id_by_set_spec.return_value = []
        mock_get_all_by_template.return_value = []
        data = {'verb': 'ListIdentifiers', 'metadataPrefix': 'dummy', 'set': 'dummy_set'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.NoRecordsMatch))
        self.check_tag_error_code(response.rendered_content, exceptions.NO_RECORDS_MATCH)


class TestListMetadataFormats(TestOaiPmhSuite):
    @patch.object(oai_provider_metadata_format_api, 'get_all')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_metadata_format_no_data(self, mock_get, mock_request, mock_get_all):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_all.return_value = []
        data = {'verb': 'ListMetadataFormats'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.NoMetadataFormat))
        self.check_tag_error_code(response.rendered_content, exceptions.NO_METADATA_FORMAT)

    @patch.object(oai_provider_metadata_format_api, 'get_all')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_metadata_format_bad_identifier(self, mock_get, mock_request, mock_get_all):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_all.return_value = []
        data = {'verb': 'ListMetadataFormats', 'identifier': 'dummy'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.IdDoesNotExist))
        self.check_tag_error_code(response.rendered_content, exceptions.ID_DOES_NOT_EXIST)

    @patch.object(data_api, 'get_by_id')
    @patch.object(CheckOaiPmhRequest, 'check_identifier')
    @patch.object(oai_provider_metadata_format_api, 'get_all')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_metadata_format_identifier_does_not_exist(self, mock_get, mock_request, mock_get_all,
                                                            mock_check_identifier, mock_get_by_id):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_all.return_value = []
        mock_check_identifier.return_value = ObjectId()
        mock_get_by_id.side_effect = common_exceptions.DoesNotExist('')
        data = {'verb': 'ListMetadataFormats', 'identifier': 'dummy'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.IdDoesNotExist))
        self.check_tag_error_code(response.rendered_content, exceptions.ID_DOES_NOT_EXIST)

    @patch.object(oai_provider_metadata_format_api, 'get_metadata_format_schema_url')
    @patch.object(oai_provider_metadata_format_api, 'get_all')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_metadata_format_identifier(self, mock_get, mock_request, mock_get_all,
                                             mock_get_metadata_format_schema_url):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        list_metadata_formats = [_create_mock_oai_metadata_format(), _create_mock_oai_metadata_format()]
        mock_get_all.return_value = list_metadata_formats
        mock_get_metadata_format_schema_url.return_value = "dummy_schema"
        data = {'verb': 'ListMetadataFormats'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListMetadataFormats')
        self.check_tag_count(response.rendered_content, 'metadataFormat', len(list_metadata_formats))

    @patch.object(oai_provider_metadata_format_api, 'get_metadata_format_schema_url')
    @patch.object(oai_xsl_template_api, 'get_metadata_formats_by_templates')
    @patch.object(oai_provider_metadata_format_api, 'get_all_by_templates')
    @patch.object(data_api, 'get_by_id')
    @patch.object(CheckOaiPmhRequest, 'check_identifier')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_metadata_format_identifier_with_identifier(self, mock_get, mock_request,
                                                             mock_check_identifier,
                                                             mock_get_by_id,
                                                             mock_get_all_by_templates,
                                                             mock_get_get_metadata_formats_by_templates,
                                                             mock_get_metadata_format_schema_url):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_check_identifier.return_value = ObjectId()
        mock_get_by_id.return_value.template = ObjectId()
        list_metadata_formats = [_create_mock_oai_metadata_format()]
        mock_get_all_by_templates.return_value = list_metadata_formats
        mock_get_get_metadata_formats_by_templates.return_value = []
        mock_get_metadata_format_schema_url.return_value = "dummy_schema"
        data = {'verb': 'ListMetadataFormats', 'identifier': "test_identifier"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_tag_exist(response.rendered_content, 'ListMetadataFormats')
        self.check_tag_count(response.rendered_content, 'metadataFormat', len(list_metadata_formats))


class TestGetRecord(TestOaiPmhSuite):
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_missing_identifier(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        data = {'verb': 'GetRecord', 'metadataPrefix': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_missing_metadata_prefix(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        data = {'verb': 'GetRecord', 'identifier': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_bad_identifier(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        data = {'verb': 'GetRecord', 'metadataPrefix': "dummy", 'identifier': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.IdDoesNotExist))
        self.check_tag_error_code(response.rendered_content, exceptions.ID_DOES_NOT_EXIST)

    @patch.object(oai_data_api, 'get_by_data')
    @patch.object(CheckOaiPmhRequest, 'check_identifier')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_identifier_does_not_exist(self, mock_get, mock_request, mock_check_identifier, mock_get_by_data):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_check_identifier.return_value = ObjectId()
        mock_get_by_data.side_effect = common_exceptions.DoesNotExist('')
        data = {'verb': 'GetRecord', 'metadataPrefix': "dummy", 'identifier': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.IdDoesNotExist))
        self.check_tag_error_code(response.rendered_content, exceptions.ID_DOES_NOT_EXIST)

    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(oai_data_api, 'get_by_data')
    @patch.object(CheckOaiPmhRequest, 'check_identifier')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_metadata_format_does_not_exist(self, mock_get, mock_request, mock_check_identifier,
                                                       mock_get_by_data, mock_get_by_metadata_prefix):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_check_identifier.return_value = ObjectId()
        mock_get_by_data.return_value = object()
        mock_get_by_metadata_prefix.side_effect = common_exceptions.DoesNotExist("")
        data = {'verb': 'GetRecord', 'metadataPrefix': "dummy", 'identifier': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.CannotDisseminateFormat))
        self.check_tag_error_code(response.rendered_content, exceptions.DISSEMINATE_FORMAT)

    @patch.object(oai_provider_set_api, 'get_all_by_template_ids')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(oai_data_api, 'get_by_data')
    @patch.object(CheckOaiPmhRequest, 'check_identifier')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_with_xml_decl_use_raw(self, mock_get, mock_request, mock_check_identifier,
                                              mock_get_by_data, mock_get_by_metadata_prefix,
                                              mock_get_all_by_template_ids):
        # Arrange
        xml_decl = "<?xml version='1.0' encoding='UTF-8'?>"
        mock_oai_template = Mock(spec=Template)
        mock_oai_template.id = ObjectId()

        mock_metadata_format = Mock(spec=OaiProviderMetadataFormat)
        mock_metadata_format.is_template = True
        mock_metadata_format.template = mock_oai_template

        mock_oai_data = Mock(spec=OaiData)
        mock_oai_data.status = oai_status.ACTIVE
        mock_oai_data.template = mock_oai_template
        mock_oai_data.data.xml_content = """
            %s
            <body>
                <tag01>value_a</tag01>
                <tag02>value_b</tag02>
            </body>
        """ % xml_decl
        mock_oai_data.oai_date_stamp = datetime(2019, 4, 1)

        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_check_identifier.return_value = ObjectId()
        mock_get_by_data.return_value = mock_oai_data
        mock_get_by_metadata_prefix.return_value = mock_metadata_format
        mock_get_all_by_template_ids.return_value = ""
        data = {'verb': 'GetRecord', 'metadataPrefix': "dummy", 'identifier': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)
        output_xml_data = response.context_data["XML"]

        # Assert
        self.assertNotIn(xml_decl, output_xml_data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch.object(xsl_transformation_api, 'xsl_transform')
    @patch.object(oai_xsl_template_api, 'get_by_template_id_and_metadata_format_id')
    @patch.object(oai_provider_set_api, 'get_all_by_template_ids')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(oai_data_api, 'get_by_data')
    @patch.object(CheckOaiPmhRequest, 'check_identifier')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_get_record_with_xml_decl_not_raw(self, mock_get, mock_request, mock_check_identifier,
                                              mock_get_by_data, mock_get_by_metadata_prefix,
                                              mock_get_all_by_template_ids,
                                              mock_get_by_template_id_and_metadata_format_id,
                                              mock_xsl_transform):
        # Arrange
        xml_decl = "<?xml version='1.0' encoding='UTF-8'?>"
        mock_cleaned_xml = """
            <body>
                <tag01>value_a</tag01>
                <tag02>value_b</tag02>
            </body>
        """
        mock_oai_template = Mock(spec=Template)
        mock_oai_template.id = ObjectId()

        mock_metadata_format = Mock(spec=OaiProviderMetadataFormat)
        mock_metadata_format.is_template = False  # Will trigger use_raw = False
        mock_metadata_format.template = mock_oai_template

        mock_oai_data = Mock(spec=OaiData)
        mock_oai_data.status = oai_status.ACTIVE
        mock_oai_data.template = mock_oai_template
        mock_oai_data.data.xml_content = """
            %s
            %s
        """ % (xml_decl, mock_cleaned_xml)
        mock_oai_data.oai_date_stamp = datetime(2019, 4, 1)

        mock_oai_xslt = Mock(spec=OaiXslTemplate)
        mock_xslt = Mock(spec=XslTransformation)
        mock_xslt.name = "dummy"
        mock_oai_xslt.xslt = mock_xslt

        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_check_identifier.return_value = ObjectId()
        mock_get_by_data.return_value = mock_oai_data
        mock_get_by_metadata_prefix.return_value = mock_metadata_format
        mock_get_all_by_template_ids.return_value = ""
        mock_get_by_template_id_and_metadata_format_id.return_value = mock_oai_xslt
        mock_xsl_transform.return_value = mock_cleaned_xml

        data = {'verb': 'GetRecord', 'metadataPrefix': "dummy", 'identifier': "dummy"}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)
        output_xml_data = response.context_data["XML"]

        # Assert
        self.assertNotIn(xml_decl, output_xml_data)
        self.assertEqual(response.status_code, HTTP_200_OK)


class TestListRecords(TestOaiPmhSuite):
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_records_error_metadata_prefix_missing(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        bad_arg = {'verb': ['ListRecords']}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_records_error_date_until(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        bad_arg = {'verb': 'ListRecords', 'metadataPrefix': 'dummy', 'from': 'bad_date'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_records_error_date_from(self, mock_get, mock_request):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        bad_arg = {'verb': 'ListRecords', 'metadataPrefix': 'dummy', 'until': 'bad_date'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.BadArgument))
        self.check_tag_error_code(response.rendered_content, exceptions.BAD_ARGUMENT)

    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_records_no_metadata_format(self, mock_get, mock_request, mock_get_by_metadata_prefix):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_by_metadata_prefix.side_effect = common_exceptions.DoesNotExist('')
        bad_arg = {'verb': 'ListRecords', 'metadataPrefix': 'dummy'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=bad_arg)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.CannotDisseminateFormat))
        self.check_tag_error_code(response.rendered_content, exceptions.DISSEMINATE_FORMAT)

    @patch.object(oai_provider_set_api, 'get_by_set_spec')
    @patch.object(oai_xsl_template_api, 'get_template_ids_by_metadata_format')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(OAIProviderView, '_get_templates_id_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_records_no_set_or_bad_set(self, mock_get, mock_request, mock_get_templates_id,
                                            mock_get_by_metadata_prefix, mock_get_template_ids,
                                            mock_get_by_set_spec):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_templates_id.return_value = []
        mock_get_by_metadata_prefix.return_value = []
        mock_get_template_ids.return_value = [ObjectId()]
        mock_get_by_set_spec.side_effect = common_exceptions.DoesNotExist('')
        data = {'verb': 'ListRecords', 'metadataPrefix': 'dummy', 'set': 'dummy_set'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.NoRecordsMatch))
        self.check_tag_error_code(response.rendered_content, exceptions.NO_RECORDS_MATCH)

    @patch.object(oai_data_api, 'get_all_by_template')
    @patch.object(OAIProviderView, '_get_templates_id_by_set_spec')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(OAIProviderView, '_get_templates_id_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_records_no_xml_data(self, mock_get, mock_request, mock_get_templates_id,
                                      mock_get_by_metadata_prefix, mock_get_templates_id_by_set_spec,
                                      mock_get_all_by_template):
        # Arrange
        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_templates_id.return_value = [ObjectId()]
        mock_get_by_metadata_prefix.return_value = []
        mock_get_templates_id_by_set_spec.return_value = []
        mock_get_all_by_template.return_value = []
        data = {'verb': 'ListRecords', 'metadataPrefix': 'dummy', 'set': 'dummy_set'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)

        # Assert
        self.assertTrue(isinstance(response.context_data['errors'][0], exceptions.NoRecordsMatch))
        self.check_tag_error_code(response.rendered_content, exceptions.NO_RECORDS_MATCH)

    @patch.object(oai_provider_set_api, 'get_all_by_template_ids')
    @patch.object(oai_data_api, 'get_all_by_template')
    @patch.object(OAIProviderView, '_get_templates_id_by_set_spec')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(OAIProviderView, '_get_templates_id_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_record_with_xml_decl_use_raw(self, mock_get, mock_request, mock_get_templates_id,
                                               mock_get_by_metadata_prefix,
                                               mock_get_templates_id_by_set_spec,
                                               mock_get_all_by_template,
                                               mock_get_all_by_template_ids):
        # Arrange
        xml_decl = "<?xml version='1.0' encoding='UTF-8'?>"

        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_templates_id.return_value = [ObjectId()]
        mock_get_by_metadata_prefix.return_value = []
        mock_get_templates_id_by_set_spec.return_value = []

        mock_oai_data = Mock(spec=OaiData)
        mock_oai_data.status = oai_status.ACTIVE
        # mock_oai_data.template = mock_oai_template
        mock_oai_data.data.xml_content = """
            %s
            <body>
                <tag01>value_a</tag01>
                <tag02>value_b</tag02>
            </body>
        """ % xml_decl
        mock_oai_data.oai_date_stamp = datetime(2019, 4, 1)

        mock_get_all_by_template.return_value = [mock_oai_data]
        mock_get_all_by_template_ids.return_value = []

        data = {'verb': 'ListRecords', 'metadataPrefix': 'dummy', 'set': 'dummy_set'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)
        output_xml_data = response.context_data["items"][0]["XML"]

        # Assert
        self.assertNotIn(xml_decl, output_xml_data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch.object(xsl_transformation_api, 'xsl_transform')
    @patch.object(oai_provider_set_api, 'get_all_by_template_ids')
    @patch.object(oai_data_api, 'get_all_by_template')
    @patch.object(oai_xsl_template_api, 'get_by_template_id_and_metadata_format_id')
    @patch.object(OAIProviderView, '_get_templates_id_by_set_spec')
    @patch.object(oai_provider_metadata_format_api, 'get_by_metadata_prefix')
    @patch.object(oai_xsl_template_api, 'get_template_ids_by_metadata_format')
    @patch.object(OAIProviderView, '_get_templates_id_by_metadata_prefix')
    @patch.object(HttpRequest, 'build_absolute_uri')
    @patch.object(oai_settings_api, 'get')
    def test_list_record_with_xml_decl_not_raw(self, mock_get, mock_request, mock_get_templates_id,
                                               mock_get_template_ids_by_metadata_format,
                                               mock_get_by_metadata_prefix,
                                               mock_get_templates_id_by_set_spec,
                                               mock_get_by_template_id_and_metadata_format_id,
                                               mock_get_all_by_template,
                                               mock_get_all_by_template_ids, mock_xsl_transform):
        # Arrange
        xml_decl = "<?xml version='1.0' encoding='UTF-8'?>"
        mock_cleaned_xml = """
            <body>
                <tag01>value_a</tag01>
                <tag02>value_b</tag02>
            </body>
        """

        mock_get.return_value = _create_mock_oai_settings()
        mock_request.return_value = ""
        mock_get_templates_id.return_value = []
        mock_get_template_ids_by_metadata_format.return_value = [ObjectId()]
        mock_get_by_metadata_prefix.return_value = []
        mock_get_templates_id_by_set_spec.return_value = []

        mock_oai_xslt = Mock(spec=OaiXslTemplate)
        mock_xslt = Mock(spec=XslTransformation)
        mock_xslt.name = "dummy"
        mock_oai_xslt.xslt = mock_xslt

        mock_get_by_template_id_and_metadata_format_id.return_value = mock_oai_xslt

        mock_oai_data = Mock(spec=OaiData)
        mock_oai_data.status = oai_status.ACTIVE
        # mock_oai_data.template = mock_oai_template
        mock_oai_data.data.xml_content = """
            %s
            %s
        """ % (xml_decl, mock_cleaned_xml)
        mock_oai_data.oai_date_stamp = datetime(2019, 4, 1)

        mock_get_all_by_template.return_value = [mock_oai_data]
        mock_get_all_by_template_ids.return_value = []
        mock_xsl_transform.return_value = mock_cleaned_xml

        data = {'verb': 'ListRecords', 'metadataPrefix': 'dummy', 'set': 'dummy_set'}

        # Act
        response = RequestMock.do_request_get(OAIProviderView.as_view(), None, data=data)
        output_xml_data = response.context_data["items"][0]["XML"]

        # Assert
        self.assertNotIn(xml_decl, output_xml_data)
        self.assertEqual(response.status_code, HTTP_200_OK)


def _create_mock_oai_settings():
    """ Mock an OaiSettings.

        Returns:
            OaiSettings mock.

    """
    mock_oai_settings = Mock(spec=OaiSettings)
    _set_oai_setting_fields(mock_oai_settings)

    return mock_oai_settings


def _create_mock_oai_sets():
    """ Mock an OaiSet.

        Returns:
            OaiProviderSet mock.

    """
    mock_oai_sets = Mock(spec=OaiProviderSet)
    mock_oai_sets.set_spec = "set_spec"
    mock_oai_sets.set_name = "set_name"
    mock_oai_sets.description = "Description"

    return mock_oai_sets


def _create_mock_oai_metadata_format():
    """ Mock an OaiMetadataFormat.

        Returns:
            OaiProviderMetadataFormat mock.

    """
    mock_oai_metadata_format = Mock(spec=OaiProviderMetadataFormat)
    mock_oai_metadata_format.metadata_namespace = "namespace"
    mock_oai_metadata_format.metadata_prefix = "dummy"

    return mock_oai_metadata_format


def _set_oai_setting_fields(oai_settings):
    """ Set OaiSettings fields.

        Args:
            oai_settings:

        Returns:
            OaiSettings with assigned fields.

    """
    oai_settings.repository_name = "Repository"
    oai_settings.repository_identifier = "identifier"
    oai_settings.enable_harvesting = True

    return oai_settings
