""" Authentication tests for OAI Provider Metadata Format REST API
"""
from django.http import HttpResponse
from django.test import SimpleTestCase
from mock import Mock
from mock.mock import patch
from rest_framework import status

from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import OaiProviderMetadataFormat
from core_oaipmh_provider_app.components.oai_xsl_template.models import OaiXslTemplate
from core_oaipmh_provider_app.rest.oai_provider_metadata_format import views as metadata_format_views
from core_oaipmh_provider_app.rest.serializers import OaiProviderMetadataFormatSerializer, \
    UpdateMetadataFormatSerializer, TemplateMetadataFormatSerializer, TemplateToMFMappingXSLTSerializer, \
    TemplateToMFUnMappingXSLTSerializer


class MetadataFormatsListGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            metadata_format_views.MetadataFormatsList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            metadata_format_views.MetadataFormatsList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiProviderMetadataFormat, "get_all")
    @patch.object(OaiProviderMetadataFormatSerializer, "data")
    def test_staff_returns_http_200(self, oai_provider_metadata_format_serializer_data,
                                    oai_provider_metadata_format_get_all):
        oai_provider_metadata_format_serializer_data.return_value = True
        oai_provider_metadata_format_get_all.return_value = {}
        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            metadata_format_views.MetadataFormatsList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MetadataFormatsListPostPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            metadata_format_views.MetadataFormatsList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_post(
            metadata_format_views.MetadataFormatsList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiProviderMetadataFormatSerializer, "is_valid")
    @patch.object(OaiProviderMetadataFormatSerializer, "save")
    @patch.object(OaiProviderMetadataFormatSerializer, "data")
    def test_staff_returns_http_201(self, oai_provider_metadata_format_serializer_data,
                                    oai_provider_metadata_format_serializer_save,
                                    oai_provider_metadata_format_serializer_is_valid):
        oai_provider_metadata_format_serializer_data.return_value = True
        # method returns serializer.save directly (which returns an HTTPResponse with status code 201 automatically)
        oai_provider_metadata_format_serializer_save.return_value = _create_mock_http_response(status.HTTP_201_CREATED)
        oai_provider_metadata_format_serializer_is_valid.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_post(
            metadata_format_views.MetadataFormatsList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class MetadataFormatsDetailGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            metadata_format_views.MetadataFormatDetail.as_view(),
            None,
            param={'set_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            metadata_format_views.MetadataFormatDetail.as_view(),
            mock_user,
            param={'set_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiProviderMetadataFormat, "get_by_id")
    @patch.object(OaiProviderMetadataFormatSerializer, "data")
    def test_staff_returns_http_200(self, oai_provider_metadata_format_serializer_data,
                                    oai_provider_metadata_format_get_by_id):
        oai_provider_metadata_format_serializer_data.return_value = True
        oai_provider_metadata_format_get_by_id.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            metadata_format_views.MetadataFormatDetail.as_view(),
            mock_user,
            param={'metadata_format_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MetadataFormatsDetailDeletePermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_delete(
            metadata_format_views.MetadataFormatDetail.as_view(),
            None,
            param={'set_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_delete(
            metadata_format_views.MetadataFormatDetail.as_view(),
            mock_user,
            param={'set_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiProviderMetadataFormat, "get_by_id")
    @patch.object(OaiProviderMetadataFormat, "delete")
    def test_staff_returns_http_204(self, oai_provider_metadata_format_delete,
                                    oai_provider_metadata_format_get_by_id):
        oai_provider_metadata_format_delete.return_value = True
        oai_provider_metadata_format_get_by_id.return_value = _create_mock_oai_provider_metadata_format()

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_delete(
            metadata_format_views.MetadataFormatDetail.as_view(),
            mock_user,
            param={'metadata_format_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class MetadataFormatsDetailPatchPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_patch(
            metadata_format_views.MetadataFormatDetail.as_view(),
            None,
            param={'set_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_patch(
            metadata_format_views.MetadataFormatDetail.as_view(),
            mock_user,
            param={'set_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(OaiProviderMetadataFormat, "get_by_id")
    @patch.object(UpdateMetadataFormatSerializer, "is_valid")
    @patch.object(UpdateMetadataFormatSerializer, "save")
    def test_staff_returns_http_200(self, update_metadata_format_serializer_save,
                                    update_metadata_format_serializer_is_valid,
                                    oai_provider_metadata_format_get_by_id):
        update_metadata_format_serializer_save.return_value = None
        update_metadata_format_serializer_is_valid.return_value = {}
        oai_provider_metadata_format_get_by_id.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_patch(
            metadata_format_views.MetadataFormatDetail.as_view(),
            mock_user,
            param={'metadata_format_id': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TemplateAsMetadataFormatPostPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            metadata_format_views.TemplateAsMetadataFormat.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_post(
            metadata_format_views.TemplateAsMetadataFormat.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(TemplateMetadataFormatSerializer, "is_valid")
    @patch.object(TemplateMetadataFormatSerializer, "save")
    def test_staff_returns_http_201(self, template_metadata_format_serializer_save,
                                    template_metadata_format_serializer_is_valid):
        # method returns serializer.save directly (which returns an HTTPResponse with status code 201 automatically)
        template_metadata_format_serializer_save.return_value = _create_mock_http_response(status.HTTP_201_CREATED)
        template_metadata_format_serializer_is_valid.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_post(
            metadata_format_views.TemplateAsMetadataFormat.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TemplateMetadataFormatXSLTPostPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_post(
            metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(TemplateToMFMappingXSLTSerializer, "is_valid")
    @patch.object(TemplateToMFMappingXSLTSerializer, "save")
    @patch.object(TemplateToMFMappingXSLTSerializer, "init_instance")
    def test_staff_returns_http_200(self, template_to_mf_mapping_xslt_serializer_init_instance,
                                    template_to_mf_mapping_xslt_serializer_save,
                                    template_to_mf_mapping_xslt_serializer_is_valid):
        template_to_mf_mapping_xslt_serializer_save.return_value = None
        template_to_mf_mapping_xslt_serializer_is_valid.return_value = {}
        template_to_mf_mapping_xslt_serializer_init_instance.return_value = None

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_post(
            metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TemplateMetadataFormatXSLTDeletePermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_delete(
            metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_delete(
            metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(TemplateToMFUnMappingXSLTSerializer, "is_valid")
    @patch.object(TemplateToMFUnMappingXSLTSerializer, "save")
    @patch.object(TemplateToMFUnMappingXSLTSerializer, "data")
    @patch.object(OaiXslTemplate, "get_by_template_id_and_metadata_format_id")
    @patch.object(OaiXslTemplate, "delete")
    def test_staff_returns_http_204(self, oai_xsl_template_delete,
                                    oai_xsl_template_get_by_template_id_and_metadata_format_id,
                                    template_to_mf_mapping_xslt_serializer_data,
                                    template_to_mf_mapping_xslt_serializer_save,
                                    template_to_mf_mapping_xslt_serializer_is_valid):
        # method returns serializer.save directly (which returns an HTTPResponse with status code 201 automatically)
        template_to_mf_mapping_xslt_serializer_save.return_value = _create_mock_http_response(status.HTTP_201_CREATED)
        template_to_mf_mapping_xslt_serializer_is_valid.return_value = {}
        template_to_mf_mapping_xslt_serializer_data.return_value = {'template_id': 'id1',
                                                                    'metadata_format_id': 'id2'}
        oai_xsl_template_get_by_template_id_and_metadata_format_id.return_value = _create_mock_oai_xsl_template()
        oai_xsl_template_delete.return_value = None

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_delete(
            metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


def _create_mock_http_response(status_code):
    """ Return a mock HTTP Response

    Args:
        status_code:

    Returns:

    """
    mock_response = HttpResponse()
    mock_response.status_code = status_code
    return mock_response


def _create_mock_oai_provider_metadata_format():
    """ Return a mock Oai Provider Metadata Format

    Returns:

    """
    mock_oai_provider_metadata_format = Mock(spec=OaiProviderMetadataFormat)
    return mock_oai_provider_metadata_format


def _create_mock_oai_xsl_template():
    """ Return a mock Oai XSL Template

    Returns:

    """
    mock_oai_xsl_template = Mock(spec=OaiXslTemplate)
    return mock_oai_xsl_template
