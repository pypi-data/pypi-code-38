from unittest.case import TestCase
from bson.objectid import ObjectId
from mock.mock import Mock, patch
import core_oaipmh_provider_app.components.oai_data.api as oai_data_api
from core_oaipmh_provider_app.components.oai_data.models import OaiData
from core_main_app.commons import exceptions
from datetime import datetime
from core_oaipmh_provider_app.commons import status
from core_main_app.components.template.models import Template
from core_main_app.components.data.models import Data


class TestOaiDataUpsert(TestCase):
    def setUp(self):
        self.mock_oai_data = _create_oai_data()

    @patch.object(OaiData, 'save')
    def test_oai_data_upsert_returns_object(self, mock_save):
        # Arrange
        mock_save.return_value = self.mock_oai_data

        # Act
        result = oai_data_api.upsert(self.mock_oai_data)

        # Assert
        self.assertIsInstance(result, OaiData)

    @patch.object(OaiData, 'save')
    def test_oai_data_upsert_raises_error_if_save_failed(self, mock_save):
        # Arrange
        mock_save.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(Exception):
            oai_data_api.upsert(self.mock_oai_data)


class TestOaiDataDelete(TestCase):
    @patch.object(OaiData, 'delete')
    def test_delete_oai_data_raises_exception_if_error(self, mock_delete):
        # Arrange
        oai_data = _create_oai_data()
        mock_delete.side_effect = Exception()

        # Act # Assert
        with self.assertRaises(Exception):
            oai_data_api.delete(oai_data)


class TestOaiDataGetById(TestCase):
    @patch.object(OaiData, 'get_by_id')
    def test_get_by_id_returns_object(self, mock_get_by_id):
        # Arrange
        mock_oai_data = _create_oai_data()
        mock_oai_data.id = ObjectId()

        mock_get_by_id.return_value = mock_oai_data

        # Act
        result = oai_data_api.get_by_id(mock_get_by_id.id)

        # Assert
        self.assertIsInstance(result, OaiData)

    @patch.object(OaiData, 'get_by_id')
    def test_get_by_id_raises_exception_if_object_does_not_exist(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_id.side_effect = exceptions.DoesNotExist("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            oai_data_api.get_by_id(mock_absent_id)

    @patch.object(OaiData, 'get_by_id')
    def test_get_by_id_raises_exception_if_internal_error(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()

        mock_get_by_id.side_effect = exceptions.ModelError("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            oai_data_api.get_by_id(mock_absent_id)


class TestOaiDataGetByData(TestCase):
    @patch.object(OaiData, 'get_by_data')
    def test_get_by_data_returns_object(self, mock_get_by_data):
        # Arrange
        mock_oai_data = _create_oai_data()
        mock_oai_data.data = Data()

        mock_get_by_data.return_value = mock_oai_data

        # Act
        result = oai_data_api.get_by_data(mock_get_by_data.data)

        # Assert
        self.assertIsInstance(result, OaiData)

    @patch.object(OaiData, 'get_by_data')
    def test_get_by_data_raises_exception_if_object_does_not_exist(self, mock_get_by_data):
        # Arrange
        mock_absent_data = Data()

        mock_get_by_data.side_effect = exceptions.DoesNotExist("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            oai_data_api.get_by_data(mock_absent_data)

    @patch.object(OaiData, 'get_by_data')
    def test_get_by_data_raises_exception_if_internal_error(self, mock_get_by_data):
        # Arrange
        mock_absent_data = Data()

        mock_get_by_data.side_effect = exceptions.ModelError("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            oai_data_api.get_by_data(mock_absent_data)


class TestOaiDataGetAll(TestCase):
    @patch.object(OaiData, 'get_all')
    def test_get_all_contains_only_oai_data(self, mock_get_all):
        _generic_get_all_test(self, mock_get_all, oai_data_api.get_all())


class TestOaiDataGetAllByTemplate(TestCase):
    @patch.object(OaiData, 'get_all_by_template')
    def test_get_all_by_temlate_contains_only_oai_data(self, mock_get_all):
        _generic_get_all_test(self, mock_get_all, oai_data_api.get_all_by_template(Template()))


class TestOaiDataGetAllByStatus(TestCase):
    @patch.object(OaiData, 'get_all_by_status')
    def test_get_all_by_status_contains_only_oai_data(self, mock_get_all):
        _generic_get_all_test(self, mock_get_all, oai_data_api.get_all_by_status(status.ACTIVE))


class TestOaiDataGetEarliestDataDate(TestCase):
    @patch.object(OaiData, 'get_earliest_data_date')
    def test_get_earliest_data_date_raises_exception_if_internal_error(self, mock_get_earliest_data_date):
        # Arrange
        mock_absent_data = Data()

        mock_get_earliest_data_date.side_effect = exceptions.ModelError("Error.")

        # Act + Assert
        with self.assertRaises(exceptions.ModelError):
            oai_data_api.get_by_data(mock_absent_data)


def _generic_get_all_test(self, mock_get_all, act_function):
    # Arrange
    mock_oai_data1 = _create_mock_oai_data()
    mock_oai_data2 = _create_mock_oai_data()

    mock_get_all.return_value = [mock_oai_data1, mock_oai_data2]

    # Act
    result = act_function

    # Assert
    self.assertTrue(all(isinstance(item, OaiData) for item in result))


def _create_oai_data():
    """ Get an OaiData object.

    Returns:
        OaiData instance.

    """
    oai_data = OaiData()
    oai_data = _set_oai_data_fields(oai_data)

    return oai_data


def _create_mock_oai_data():
    """ Mock an OaiData.

    Returns:
        OaiData mock.

    """
    mock_oai_data = Mock(spec=OaiData)
    mock_oai_data = _set_oai_data_fields(mock_oai_data)

    return mock_oai_data


def _set_oai_data_fields(oai_data):
    """ Set OaiData fields.

    Returns:
        OaiData with assigned fields.

    """
    oai_data.status = status.ACTIVE
    oai_data.data = Data()
    oai_data.template = Template()
    oai_data.oai_date_stamp = datetime.now()

    return oai_data
