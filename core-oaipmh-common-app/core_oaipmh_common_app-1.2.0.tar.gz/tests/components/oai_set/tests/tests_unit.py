from unittest.case import TestCase
from bson.objectid import ObjectId
from mock.mock import Mock, patch
import core_oaipmh_common_app.components.oai_set.api as set_api
from core_main_app.commons import exceptions
from core_oaipmh_common_app.components.oai_set.models import OaiSet


class TestOaiSetGetById(TestCase):
    @patch.object(OaiSet, 'get_by_id')
    def test_oai_set_get_by_id_return_object(self, mock_get_by_id):
        # Arrange
        mock_oai_set = _create_mock_oai_set()

        mock_get_by_id.return_value = mock_oai_set

        # Act
        result = set_api.get_by_id(mock_get_by_id.id)

        # Assert
        self.assertIsInstance(result, OaiSet)

    @patch.object(OaiSet, 'get_by_id')
    def test_oai_set_get_by_id_raises_exception_if_object_does_not_exist(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_id.side_effect = exceptions.DoesNotExist("Error")

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            set_api.get_by_id(mock_absent_id)

    @patch.object(OaiSet, 'get_by_id')
    def test_oai_set_get_by_id_raises_exception_if_internal_error(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_id.side_effect = exceptions.ModelError("Error")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            set_api.get_by_id(mock_absent_id)


class TestOaiSetGetBySetSpec(TestCase):
    @patch.object(OaiSet, 'get_by_set_spec')
    def test_oai_set_get_by_set_spec_return_object(self, mock_get_by_set_spec):
        # Arrange
        mock_oai_set = _create_mock_oai_set()

        mock_get_by_set_spec.return_value = mock_oai_set

        # Act
        result = set_api.get_by_set_spec(mock_get_by_set_spec.setSpec)

        # Assert
        self.assertIsInstance(result, OaiSet)

    @patch.object(OaiSet, 'get_by_set_spec')
    def test_oai_set_get_by_set_spec_raises_exception_if_object_does_not_exist(self, mock_get_by_set_spec):
        # Arrange
        mock_absent_set_spec = "oai_test"

        mock_get_by_set_spec.side_effect = exceptions.DoesNotExist("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            set_api.get_by_set_spec(mock_absent_set_spec)

    @patch.object(OaiSet, 'get_by_set_spec')
    def test_oai_set_get_by_set_spec_raises_exception_if_internal_error(self, mock_get_by_set_spec):
        # Arrange
        mock_absent_set_spec = "oai_test"

        mock_get_by_set_spec.side_effect = exceptions.ModelError("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            set_api.get_by_set_spec(mock_absent_set_spec)


class TestOaiSetGetAll(TestCase):
    @patch.object(OaiSet, 'get_all')
    def test_oai_set_get_all_contains_only_oai_set(self, mock_get_all):
        # Arrange
        mock_oai_set1 = _create_mock_oai_set()
        mock_oai_set2 = _create_mock_oai_set()

        mock_get_all.return_value = [mock_oai_set1, mock_oai_set2]

        # Act
        result = set_api.get_all()

        # Assert
        self.assertTrue(all(isinstance(item, OaiSet) for item in result))


class TestOaiSetGetAllByListIds(TestCase):
    @patch.object(OaiSet, 'get_all_by_list_ids')
    def test_oai_set_get_all_by_list_ids_contains_only_oai_metadata_format(self, mock_get_all):
        # Arrange
        mock_oai_set1 = _create_mock_oai_set()
        mock_oai_set2 = _create_mock_oai_set()
        list_ids = [ObjectId(), ObjectId()]

        mock_get_all.return_value = [mock_oai_set1, mock_oai_set2]

        # Act
        result = set_api.get_all_by_list_ids(list_ids)

        # Assert
        self.assertTrue(all(isinstance(item, OaiSet) for item in result))


def _create_mock_oai_set():
    """ Mock an OaiSet.

    Returns:
        OaiSet mock.

    """
    mock_oai_set = Mock(spec=OaiSet)
    mock_oai_set.set_spec = "oai_test"
    mock_oai_set.set_name = "test"
    mock_oai_set.id = ObjectId()

    return mock_oai_set
