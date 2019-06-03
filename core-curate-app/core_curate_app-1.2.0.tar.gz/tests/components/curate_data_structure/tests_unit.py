""" Unit Test Curate Data Structure
"""
import core_curate_app.components.curate_data_structure.api as curate_data_structure_api
from core_curate_app.components.curate_data_structure.models import CurateDataStructure
from core_main_app.components.template.models import Template
from unittest.case import TestCase
from mock import patch
from core_main_app.commons import exceptions


class TestCurateDataStructureGetById(TestCase):

    @patch.object(CurateDataStructure, 'get_by_id')
    def test_curate_data_structure_get_by_id_raises_does_not_exist_error_if_not_found(self, mock_get):
        # Arrange
        mock_get.side_effect = exceptions.DoesNotExist('')
        # Act # Assert
        with self.assertRaises(exceptions.DoesNotExist):
            curate_data_structure_api.get_by_id(1)

    def test_data_structure_get_by_id_raises_model_error_if_not_found(self):
        # Act # Assert
        with self.assertRaises(exceptions.ModelError):
            curate_data_structure_api.get_by_id(1)

    @patch.object(CurateDataStructure, 'get_by_id')
    def test_curate_data_structure_get_by_id_return_data_if_found(self, mock_get):
        # Arrange
        mock_data_structure = CurateDataStructure("1", Template(), "name")
        mock_get.return_value = mock_data_structure
        # Act
        result = curate_data_structure_api.get_by_id(1)
        # Assert
        self.assertIsInstance(result, CurateDataStructure)


class TestCurateDataStructureUpsert(TestCase):

    @patch.object(CurateDataStructure, 'save_object')
    def test_curate_data_structure_upsert_return_data_structure_element(self, mock_save):
        # Arrange
        mock_data_structure = CurateDataStructure("1", Template(), "name")
        mock_save.return_value = mock_data_structure
        # Act
        result = curate_data_structure_api.upsert(mock_data_structure)
        # Assert
        self.assertIsInstance(result, CurateDataStructure)


class TestCurateDataStructureGetAll(TestCase):

    @patch.object(CurateDataStructure, 'get_all')
    def test_curate_data_get_all_return_collection_of_curate_data(self, mock_list):
        # Arrange
        mock_data_1 = CurateDataStructure(user='1', template=_get_template(), name='name_title_1')
        mock_data_2 = CurateDataStructure(user='1', template=_get_template(), name='name_title_2')
        mock_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = curate_data_structure_api.get_all()
        # Assert
        self.assertTrue(all(isinstance(item, CurateDataStructure) for item in result))


class TestCurateDataStructureGetByUserIdAndTemplateId(TestCase):

    @patch.object(CurateDataStructure, 'get_all_by_user_id_and_template_id')
    def test_curate_data_structure_get_all_by_user_and_template_return_collection_of_curate_data_structure(self,
                                                                                                           mock_list):
        # Arrange
        mock_data_1 = CurateDataStructure(user='1', template=_get_template(), name='name_title_1')
        mock_data_2 = CurateDataStructure(user='1', template=_get_template(), name='name_title_2')
        mock_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = curate_data_structure_api.get_all_by_user_id_and_template_id(1, 1)
        # Assert
        self.assertTrue(all(isinstance(item, CurateDataStructure) for item in result))


class TestCurateDataStructureGetByUserIdAndTemplateIdAndName(TestCase):

    @patch.object(CurateDataStructure, 'get_by_user_id_and_template_id_and_name')
    def test_curate_data_structure_get_by_user_and_template_and_name_return_curate_data_structure(self,
                                                                                                    mock_get):
        # Arrange
        mock_data_1 = CurateDataStructure(user='1', template=_get_template(), name='name_title_1')
        mock_get.return_value = mock_data_1
        # Act
        result = curate_data_structure_api.get_by_user_id_and_template_id_and_name(1, 1, 'name_title_1')
        # Assert
        self.assertIsInstance(result, CurateDataStructure)

    @patch.object(CurateDataStructure, 'get_by_user_id_and_template_id_and_name')
    def test_curate_data_structure_get_by_user_and_template_and_name_raises_does_not_exist_error_if_not_found(self, mock_get):
        # Arrange
        mock_get.side_effect = exceptions.DoesNotExist('')
        # Act # Assert
        with self.assertRaises(exceptions.DoesNotExist):
            curate_data_structure_api.get_by_user_id_and_template_id_and_name(1, 1, 'name_title_1')

    def test_data_structure_get_by_user_and_template_and_name_raises_model_error_if_not_found(self):
        # Act # Assert
        with self.assertRaises(exceptions.ModelError):
            curate_data_structure_api.get_by_user_id_and_template_id_and_name(1, 1, 'name_title_1')


class TestCurateDataStructureGetAllByUserIdWithNoData(TestCase):

    @patch.object(CurateDataStructure, 'get_all_by_user_id_with_no_data')
    def test_curate_data_structure_get_all_by_user_id_with_no_data_return_curate_data_structure(self, mock_list):
        # Arrange
        mock_data_1 = CurateDataStructure(user='1', template=_get_template(), name='name_title_1')
        mock_data_2 = CurateDataStructure(user='1', template=_get_template(), name='name_title_2')
        mock_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = curate_data_structure_api.get_all_by_user_id_with_no_data(1)
        # Assert
        self.assertTrue(all(isinstance(item, CurateDataStructure) for item in result))


class TestCurateDataStructureGetAllExceptUserIdWithNoData(TestCase):

    @patch.object(CurateDataStructure, 'get_all_except_user_id_with_no_data')
    def test_curate_data_structure_get_all_except_user_id_with_no_data_return_curate_data_structure(self, mock_list):
        # Arrange
        mock_data_1 = CurateDataStructure(user='1', template=_get_template(), name='name_title_1')
        mock_data_2 = CurateDataStructure(user='1', template=_get_template(), name='name_title_2')
        mock_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = curate_data_structure_api.get_all_except_user_id_with_no_data(2)
        # Assert
        self.assertTrue(all(isinstance(item, CurateDataStructure) for item in result))


class TestCurateDataStructureGetAllByUserIdandTemplateIdWithNoData(TestCase):

    @patch.object(CurateDataStructure, 'get_all_by_user_id_and_template_id_with_no_data')
    def test_curate_data_structure_get_all_by_user_id_and_template_id_with_no_data_return_curate_data_structure(self,
                                                                                                                mock_list):
        # Arrange
        template = _get_template()
        mock_data_1 = CurateDataStructure(user='1', template=template, name='name_title_1')
        mock_data_2 = CurateDataStructure(user='1', template=template, name='name_title_2')
        mock_list.return_value = [mock_data_1, mock_data_2]
        # Act
        result = curate_data_structure_api.get_all_by_user_id_and_template_id_with_no_data('1', template.id)
        # Assert
        self.assertTrue(all(isinstance(item, CurateDataStructure) for item in result))


def _get_template():
    template = Template()
    template.id_field = 1
    xsd = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
          '<xs:element name="tag"></xs:element></xs:schema>'
    template.content = xsd
    return template
