"""Type unit tests
"""
from unittest.case import TestCase
from bson.objectid import ObjectId
from django.test import override_settings
from mock.mock import Mock, patch
from django.core import exceptions as django_exceptions

from core_composer_app.components.type.models import Type
from core_composer_app.components.type import api as type_api
from core_main_app.commons import exceptions


class TestTypeGet(TestCase):
    @patch.object(Type, 'get_by_id')
    def test_type_get_returns_type(self, mock_get_by_id):
        # Arrange
        type_filename = "Schema"
        mock_type = _create_mock_type(type_filename)

        mock_get_by_id.return_value = mock_type

        # Act
        result = type_api.get(mock_type.id)

        # Assert
        self.assertIsInstance(result, Type)

    @patch.object(Type, 'get_by_id')
    def test_template_get_raises_exception_if_object_does_not_exist(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()
        mock_get_by_id.side_effect = exceptions.DoesNotExist('')

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            type_api.get(mock_absent_id)


class TestTypeGetAll(TestCase):
    @patch.object(Type, 'get_all')
    def test_get_all_types_returns_types(self, mock_get_all):
        # Arrange
        mock_type1 = _create_mock_type()
        mock_type2 = _create_mock_type()

        mock_get_all.return_value = [mock_type1, mock_type2]

        # Act
        result = type_api.get_all()

        # Assert
        self.assertTrue(all(isinstance(item, Type) for item in result))


class TestTypeGetAllComplexType(TestCase):
    @patch.object(Type, 'get_all_complex_type')
    def test_get_all_types_returns_types(self, mock_get_all_complex_type):
        # Arrange
        mock_type1 = _create_mock_type()
        mock_type2 = _create_mock_type()

        mock_get_all_complex_type.return_value = [mock_type1, mock_type2]

        # Act
        result = type_api.get_all_complex_type()

        # Assert
        self.assertTrue(all(isinstance(item, Type) for item in result))


class TestTypeUpsert(TestCase):
    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(Type, 'save')
    def test_type_upsert_valid_returns_type(self, mock_save):
        type_object = _create_type()

        mock_save.return_value = type_object
        result = type_api.upsert(type_object)
        self.assertIsInstance(result, Type)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(Type, 'save')
    def test_type_upsert_invalid_filename_raises_validation_error(self, mock_save):
        type_object = _create_type(filename=1)
        mock_save.side_effect = django_exceptions.ValidationError("")
        with self.assertRaises(django_exceptions.ValidationError):
            type_api.upsert(type_object)

    @patch.object(Type, 'save')
    def test_type_upsert_invalid_core_type_raises_core_error(self, mock_save):
        type_object = _create_type(content="<schema></schema>")
        mock_save.return_value = None
        with self.assertRaises(exceptions.CoreError):
            type_api.upsert(type_object)


def _create_mock_type(filename="", content=""):
    """Returns a mock type

    Args:
        filename:
        content:

    Returns:

    """
    mock_type = Mock(spec=Type)
    mock_type.filename = filename
    mock_type.content = content
    mock_type.id = ObjectId()
    return mock_type


def _create_type(filename="", content=None):
    """Returns a type

    Args:
        filename:
        content:

    Returns:

    """
    if content is None:
        # set a valid content
        content = "<schema xmlns='http://www.w3.org/2001/XMLSchema'><simpleType name='type'>" \
                  "<restriction base='string'><enumeration value='test'/></restriction>" \
                  "</simpleType></schema>"
    return Type(
        id=ObjectId(),
        filename=filename,
        content=content
    )
