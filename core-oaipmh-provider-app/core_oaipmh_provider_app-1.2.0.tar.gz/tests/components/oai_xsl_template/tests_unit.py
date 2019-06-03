""" Unit Test OaiXslTemplate
"""

from unittest.case import TestCase
from bson.objectid import ObjectId
from mock.mock import Mock, patch
import core_oaipmh_provider_app.components.oai_xsl_template.api as oai_xsl_template_api
from core_oaipmh_provider_app.components.oai_xsl_template.models import OaiXslTemplate
from core_main_app.commons import exceptions
from core_main_app.components.xsl_transformation.models import XslTransformation
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import OaiProviderMetadataFormat
from core_main_app.components.template.models import Template


class TestOaiXslTemplateUpsert(TestCase):
    def setUp(self):
        self.mock_oai_xsl_template = _create_oai_xsl_template()

    @patch.object(OaiXslTemplate, 'save')
    def test_oai_xsl_template_upsert_returns_object(self, mock_save):
        # Arrange
        mock_save.return_value = self.mock_oai_xsl_template

        # Act
        result = oai_xsl_template_api.upsert(self.mock_oai_xsl_template)

        # Assert
        self.assertIsInstance(result, OaiXslTemplate)

    @patch.object(OaiXslTemplate, 'save')
    def test_oai_xsl_template_upsert_raises_error_if_save_failed(self, mock_save):
        # Arrange
        mock_save.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(Exception):
            oai_xsl_template_api.upsert(self.mock_oai_xsl_template)


class TestOaiXslTemplateDelete(TestCase):
    @patch.object(OaiXslTemplate, 'delete')
    def test_delete_oai_xsl_template_raises_exception_if_error(self, mock_delete):
        # Arrange
        oai_xsl_template = _create_oai_xsl_template()
        mock_delete.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(Exception):
            oai_xsl_template_api.delete(oai_xsl_template)


class TestOaiXslTemplateGetById(TestCase):
    @patch.object(OaiXslTemplate, 'get_by_id')
    def test_get_by_id_returns_object(self, mock_get_by_id):
        # Arrange
        mock_oai_xsl_template = _create_oai_xsl_template()
        mock_oai_xsl_template.id = ObjectId()

        mock_get_by_id.return_value = mock_oai_xsl_template

        # Act
        result = oai_xsl_template_api.get_by_id(mock_get_by_id.id)

        # Assert
        self.assertIsInstance(result, OaiXslTemplate)

    @patch.object(OaiXslTemplate, 'get_by_id')
    def test_get_by_id_raises_exception_if_object_does_not_exist(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_id.side_effect = exceptions.DoesNotExist("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            oai_xsl_template_api.get_by_id(mock_absent_id)

    @patch.object(OaiXslTemplate, 'get_by_id')
    def test_get_by_id_raises_exception_if_internal_error(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_id.side_effect = exceptions.ModelError("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            oai_xsl_template_api.get_by_id(mock_absent_id)


class TestOaiXslTemplateGetByTemplateIdAndMetadataFormatId(TestCase):
    @patch.object(OaiXslTemplate, 'get_by_template_id_and_metadata_format_id')
    def test_get_by_id_returns_object(self, mock_get_by_id_and_metadata_format_id):
        # Arrange
        mock_oai_xsl_template = _create_oai_xsl_template()
        template_id = ObjectId()
        metadata_format_id = ObjectId()

        mock_get_by_id_and_metadata_format_id.return_value = mock_oai_xsl_template

        # Act
        result = oai_xsl_template_api.get_by_template_id_and_metadata_format_id(template_id, metadata_format_id)

        # Assert
        self.assertIsInstance(result, OaiXslTemplate)

    @patch.object(OaiXslTemplate, 'get_by_template_id_and_metadata_format_id')
    def test_get_by_id_raises_exception_if_object_does_not_exist(self, mock_get_by_template_id_and_metadata_format_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_template_id_and_metadata_format_id.side_effect = exceptions.DoesNotExist("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            oai_xsl_template_api.get_by_template_id_and_metadata_format_id(mock_absent_id, mock_absent_id)

    @patch.object(OaiXslTemplate, 'get_by_template_id_and_metadata_format_id')
    def test_get_by_id_raises_exception_if_internal_error(self, mock_get_by_template_id_and_metadata_format_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_template_id_and_metadata_format_id.side_effect = exceptions.ModelError("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            oai_xsl_template_api.get_by_template_id_and_metadata_format_id(mock_absent_id, mock_absent_id)


class TestOaiXslTemplateGetAllByTemplate(TestCase):
    @patch.object(OaiXslTemplate, 'get_all_by_templates')
    def test_get_all_by_template_contains_only_oai_xsl_template(self, mock_get_all):
        _generic_get_all_test(self, mock_get_all, oai_xsl_template_api.get_all_by_templates(Template()))


class TestOaiXslTemplateGetAllByMetadataFormat(TestCase):
    @patch.object(OaiXslTemplate, 'get_all_by_metadata_format')
    def test_get_all_by_metadata_format_contains_only_oai_xsl_template(self, mock_get_all):
        _generic_get_all_test(self, mock_get_all,
                              oai_xsl_template_api.get_all_by_metadata_format(OaiProviderMetadataFormat()))


class TestOaiXslTemplateGetTemplatesIdsByMetadataFormat(TestCase):
    @patch.object(OaiXslTemplate, 'get_all_by_metadata_format')
    def test_get_template_ids_by_metadata_format(self, mock_get):
        # Arrange
        mock_oai_xsl_template1 = _create_mock_oai_xsl_template()

        mock_get.return_value = [mock_oai_xsl_template1]

        # Act
        result = oai_xsl_template_api.get_template_ids_by_metadata_format(OaiProviderMetadataFormat())

        # Assert
        self.assertEquals(mock_oai_xsl_template1.template.id, result[0])


class TestOaiXslTemplateGetMetadataFormatsByTemplates(TestCase):
    @patch.object(OaiXslTemplate, 'get_all_by_templates')
    def test_get_metadata_formats_by_templates(self, mock_get):
        # Arrange
        mock_oai_xsl_template1 = _create_mock_oai_xsl_template()

        mock_get.return_value = [mock_oai_xsl_template1]

        # Act
        result = oai_xsl_template_api.get_metadata_formats_by_templates([Template()])

        # Assert
        self.assertEquals(mock_oai_xsl_template1.oai_metadata_format, result[0])


def _generic_get_all_test(self, mock_get_all, act_function):
    # Arrange
    mock_oai_xsl_template1 = _create_mock_oai_xsl_template()
    mock_oai_xsl_template2 = _create_mock_oai_xsl_template()

    mock_get_all.return_value = [mock_oai_xsl_template1, mock_oai_xsl_template2]

    # Act
    result = act_function

    # Assert
    self.assertTrue(all(isinstance(item, OaiXslTemplate) for item in result))


def _create_oai_xsl_template():
    """ Get an OaiXslTemplate object.

    Returns:
        OaiXslTemplate instance.

    """
    oai_xsl_template = OaiXslTemplate()
    oai_xsl_template = _set_oai_xsl_template_fields(oai_xsl_template)

    return oai_xsl_template


def _create_mock_oai_xsl_template():
    """ Mock an OaiXslTemplate.

    Returns:
        OaiXslTemplate mock.

    """
    mock_oai_xsl_template = Mock(spec=OaiXslTemplate)
    mock_oai_xsl_template = _set_oai_xsl_template_fields(mock_oai_xsl_template)

    return mock_oai_xsl_template


def _set_oai_xsl_template_fields(oai_xsl_template):
    """ Set OaiXslTemplate fields.

    Returns:
        OaiXslTemplate with assigned fields.

    """
    oai_xsl_template.template = Template()
    oai_xsl_template.template.id = ObjectId()
    oai_xsl_template.xslt = XslTransformation()
    oai_xsl_template.oai_metadata_format = OaiProviderMetadataFormat()

    return oai_xsl_template
