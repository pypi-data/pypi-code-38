""" Unit Test Data Structure Element
"""
import core_parser_app.components.data_structure_element.api as data_structure_element_api
from core_parser_app.components.data_structure_element.models import DataStructureElement
from core_main_app.commons import exceptions
from unittest.case import TestCase
from mock import patch


class TestDataStructureElementGetAll(TestCase):

    @patch.object(DataStructureElement, 'get_all')
    def test_data_structure_element_get_all_return_collection_of_data(self, mock_list):
        # Arrange
        mock_data_structure_element_1 = DataStructureElement("tag", "value")
        mock_data_structure_element_2 = DataStructureElement("tag", "value")
        mock_list.return_value = [mock_data_structure_element_1, mock_data_structure_element_2]
        # Act
        result = data_structure_element_api.get_all()
        # Assert
        self.assertTrue(all(isinstance(item, DataStructureElement) for item in result))


class TestDataStructureElementGetById(TestCase):

    @patch.object(DataStructureElement, 'get_by_id')
    def test_data_structure_element_get_by_id_raises_does_not_exist_error_if_not_found(self, mock_get):
        # Arrange
        mock_get.side_effect = exceptions.DoesNotExist('')
        # Act # Assert
        with self.assertRaises(exceptions.DoesNotExist):
            data_structure_element_api.get_by_id(1)

    def test_data_structure_element_get_by_id_raises_model_error_if_not_found(self):
        # Act # Assert
        with self.assertRaises(exceptions.ModelError):
            data_structure_element_api.get_by_id(1)

    @patch.object(DataStructureElement, 'get_by_id')
    def test_data_structure_element_get_by_id_return_data_if_found(self, mock_get):
        # Arrange
        mock_data_structure_element = DataStructureElement("tag", "value")
        mock_get.return_value = mock_data_structure_element
        # Act
        result = data_structure_element_api.get_by_id(1)
        # Assert
        self.assertIsInstance(result, DataStructureElement)


class TestDataStructureElementGetAllByChildId(TestCase):

    def test_data_structure_element_get_by_id_raises_model_error_if_not_found(self):
        # Act # Assert
        with self.assertRaises(exceptions.ModelError):
            data_structure_element_api.get_all_by_child_id(1)

    @patch.object(DataStructureElement, 'get_all_by_child_id')
    def test_data_structure_element_get_all_by_id_return_data_if_found(self, mock_get):
        # Arrange
        mock_data_structure_element = DataStructureElement("tag", "value")
        mock_get.return_value = [mock_data_structure_element]
        # Act
        result = data_structure_element_api.get_all_by_child_id(1)
        # Assert
        self.assertTrue(all(isinstance(item, DataStructureElement) for item in result))


class TestDataStructureElementUpsert(TestCase):

    @patch.object(DataStructureElement, 'save')
    def test_data_structure_element_upsert_return_data_structure_element(self, mock_save):
        # Arrange
        mock_data_structure_element = DataStructureElement("tag", "value")
        mock_save.return_value = mock_data_structure_element

        # Act
        result = data_structure_element_api.upsert(mock_data_structure_element)

        # Assert
        self.assertIsInstance(result, DataStructureElement)
