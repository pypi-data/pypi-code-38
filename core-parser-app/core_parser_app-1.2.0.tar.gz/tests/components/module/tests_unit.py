from unittest.case import TestCase
from bson.objectid import ObjectId
from mock.mock import Mock, patch
from mongoengine import errors as mongoengine_errors
from django.core import exceptions as django_exceptions
from core_parser_app.components.module.models import Module
from core_parser_app.components.module import api as module_api


class TestModuleGetById(TestCase):

    @patch('core_parser_app.components.module.models.Module.get_by_id')
    def test_module_get_by_id_returns_module(self, mock_get_by_id):
        # Arrange
        mock_module = _create_mock_module()

        mock_get_by_id.return_value = mock_module

        # Act
        result = module_api.get_by_id(mock_module.id)

        # Assert
        self.assertIsInstance(result, Module)

    @patch('core_parser_app.components.module.models.Module.get_by_id')
    def test_module_get_by_id_raises_exception_if_object_does_not_exist(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()
        mock_get_by_id.side_effect = mongoengine_errors.DoesNotExist

        # Act + Assert
        with self.assertRaises(mongoengine_errors.DoesNotExist):
            module_api.get_by_id(mock_absent_id)


class TestModuleGetByUrl(TestCase):

    @patch('core_parser_app.components.module.models.Module.get_by_url')
    def test_module_get_by_url_returns_module(self, mock_get_by_url):
        # Arrange
        mock_module = _create_mock_module()

        mock_get_by_url.return_value = mock_module

        # Act
        result = module_api.get_by_url(mock_module.url)

        # Assert
        self.assertIsInstance(result, Module)

    @patch('core_parser_app.components.module.models.Module.get_by_url')
    def test_module_get_by_url_raises_exception_if_object_does_not_exist(self, mock_get_by_url):
        # Arrange
        mock_absent_url = "/absent"
        mock_get_by_url.side_effect = mongoengine_errors.DoesNotExist

        # Act + Assert
        with self.assertRaises(mongoengine_errors.DoesNotExist):
            module_api.get_by_url(mock_absent_url)


class TestModuleGetAll(TestCase):
    @patch('core_parser_app.components.module.models.Module.get_all')
    def test_module_list_contains_only_module(self, mock_get_all):
        # Arrange
        mock_module_1 = _create_mock_module()
        mock_module_2 = _create_mock_module()
        mock_get_all.return_value = [mock_module_1, mock_module_2]

        # Act
        result = module_api.get_all()

        # Assert
        self.assertTrue(all(isinstance(item, Module) for item in result))


class TestModuleUpsert(TestCase):
    @patch('core_parser_app.components.module.models.Module.save')
    def test_module_upsert_valid_returns_module(self, mock_save):
        module = _create_module()

        mock_save.return_value = module
        result = module_api.upsert(module)
        self.assertIsInstance(result, Module)

    @patch('core_parser_app.components.module.models.Module.save')
    def test_module_upsert_invalid_raises_validation_error(self, mock_save):
        module = _create_module()
        mock_save.side_effect = django_exceptions.ValidationError("")
        with self.assertRaises(django_exceptions.ValidationError):
            module_api.upsert(module)


class TestModuleGetAllUrls(TestCase):
    @patch('core_parser_app.components.module.models.Module.get_all_urls')
    def test_module_list_contains_only_urls(self, mock_get_all_urls):
        # Arrange
        mock_module_1 = _create_mock_module()
        mock_module_2 = _create_mock_module()
        mock_get_all_urls.return_value = [mock_module_1.url, mock_module_2.url]

        # Act
        result = module_api.get_all_urls()

        # Assert
        self.assertTrue(all(isinstance(item, str) for item in result))


def _create_module():
    """Returns a module

    Returns:

    """
    return Module(
        id=ObjectId(),
        name="module",
        url="/module",
        view="Module.view"
    )


def _create_mock_module():
    """
    Returns a mock module
    :return:
    """
    mock_module = Mock(spec=Module)
    mock_module.name = "module"
    mock_module.url = "/module"
    mock_module.view = "Module.view"
    mock_module.id = ObjectId()
    return mock_module
