"""Type Version Manager test cases
"""
from unittest.case import TestCase
from bson.objectid import ObjectId
from django.test import override_settings
from mock.mock import Mock, patch

from core_composer_app.components.bucket.models import Bucket
from core_composer_app.components.type.models import Type
from core_composer_app.components.type_version_manager.api import get_no_buckets_types
from core_composer_app.components.type_version_manager.models import TypeVersionManager
from core_composer_app.components.type_version_manager import api as version_manager_api
from core_main_app.commons.exceptions import CoreError, ModelError, NotUniqueError

from django.core import exceptions as django_exceptions
from mongoengine import errors as mongoengine_exceptions


class TestTypeVersionManagerInsert(TestCase):
    @patch.object(TypeVersionManager, 'save')
    @patch.object(Type, 'save')
    def test_create_version_manager_raises_exception_if_type_not_supported(self, mock_save_type,
                                                                           mock_save_type_version_manager):
        # Arrange
        type_filename = "schema.xsd"
        type_content = "<schema xmlns='http://www.w3.org/2001/XMLSchema'></schema>"
        type_object = _create_type(type_filename, type_content)

        mock_save_type.return_value = type_object

        version_manager = _create_type_version_manager(title="Schema")
        mock_save_type_version_manager.return_value = version_manager

        # Act + Assert
        with self.assertRaises(CoreError):
            version_manager_api.insert(version_manager, type_object)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(TypeVersionManager, 'save')
    @patch.object(Type, 'save')
    def test_create_version_manager_returns_version_manager(self, mock_save_type,
                                                            mock_save_type_version_manager):
        # Arrange
        type_filename = "schema.xsd"
        type_content = "<schema xmlns='http://www.w3.org/2001/XMLSchema'><simpleType name='type'>" \
                       "<restriction base='string'><enumeration value='test'/></restriction>" \
                       "</simpleType></schema>"
        type_object = _create_type(type_filename, type_content)

        mock_save_type.return_value = type_object

        version_manager = _create_type_version_manager(title="Schema")
        mock_save_type_version_manager.return_value = version_manager

        # Act
        result = version_manager_api.insert(version_manager, type_object)

        # Assert
        self.assertIsInstance(result, TypeVersionManager)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(Type, 'delete')
    @patch.object(Type, 'save')
    @patch.object(TypeVersionManager, 'save')
    def test_insert_manager_raises_api_error_if_title_already_exists(self, mock_version_manager_save,
                                                                     mock_save,
                                                                     mock_delete):
        # Arrange
        type_filename = "schema.xsd"
        type_object = _create_type(type_filename)

        mock_save.return_value = type_object
        mock_delete.return_value = None
        mock_version_manager = _create_type_version_manager(title="Schema")
        mock_version_manager_save.side_effect = mongoengine_exceptions.NotUniqueError

        # Act + Assert
        with self.assertRaises(NotUniqueError):
            version_manager_api.insert(mock_version_manager, type_object)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(Type, 'save')
    def test_create_version_manager_raises_exception_if_error_in_create_type(self, mock_save):
        # Arrange
        type_filename = "schema.xsd"
        type_object = _create_type(type_filename)

        mock_version_manager = _create_mock_type_version_manager(title="Schema")
        mock_save.side_effect = django_exceptions.ValidationError("")

        # Act + Assert
        with self.assertRaises(django_exceptions.ValidationError):
            version_manager_api.insert(mock_version_manager, type_object)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(Type, 'delete')
    @patch.object(TypeVersionManager, 'save')
    @patch.object(Type, 'save')
    def test_create_version_manager_raises_exception_if_error_in_create_version_manager(self, mock_save,
                                                                                        mock_save_version_manager,
                                                                                        mock_delete):
        # Arrange
        type_filename = "Schema"
        type_object = _create_type(type_filename)

        mock_save.return_value = type_object
        version_manager = _create_type_version_manager(title="Schema")
        mock_save_version_manager.side_effect = django_exceptions.ValidationError("")
        mock_delete.return_value = None

        # Act + Assert
        with self.assertRaises(ModelError):
            version_manager_api.insert(version_manager, type_object)


class TestTypeVersionManagerGetGlobalVersions(TestCase):
    @patch.object(TypeVersionManager, 'get_global_version_managers')
    def test_get_global_version_managers_returns_types(self, mock_get_global_version_managers):
        # Arrange
        mock_type1 = _create_mock_type()
        mock_type2 = _create_mock_type()

        mock_get_global_version_managers.return_value = [mock_type1, mock_type2]

        result = version_manager_api.get_global_version_managers()

        # Assert
        self.assertTrue(all(isinstance(item, Type) for item in result))


class TestTypeVersionManagerGetVersionManagersByUser(TestCase):
    @patch.object(TypeVersionManager, 'get_version_managers_by_user')
    def test_get_version_managers_by_user_returns_types_with_given_user_id(self, mock_get_version_managers_by_user):
        # Arrange
        user_id = '10'
        mock_type1 = _create_mock_type_version_manager(user=user_id)
        mock_type2 = _create_mock_type_version_manager(user=user_id)

        mock_get_version_managers_by_user.return_value = [mock_type1, mock_type2]

        result = version_manager_api.get_version_managers_by_user(user_id)

        # Assert
        self.assertTrue(item.user_id == user_id for item in result)


class TestGetNoBucketsTypes(TestCase):
    @patch.object(TypeVersionManager, 'get_global_version_managers')
    @patch.object(Bucket, 'get_all')
    def test_get_no_buckets_types_returns_types(self, mock_get_all_buckets, mock_get_global_version_managers):
        # Arrange
        mock_type1 = _create_mock_type_version_manager()
        mock_type2 = _create_mock_type_version_manager()
        mock_get_global_version_managers.return_value = [mock_type1, mock_type2]
        mock_get_all_buckets.return_value = []

        result = get_no_buckets_types()
        self.assertTrue(all(isinstance(item, TypeVersionManager) for item in result))

    @patch.object(TypeVersionManager, 'get_global_version_managers')
    @patch.object(Bucket, 'get_all')
    def test_get_no_buckets_types_returns_all_types_if_no_buckets(self, mock_get_all_buckets,
                                                                  mock_get_global_version_managers):
        # Arrange
        mock_type1 = _create_mock_type_version_manager()
        mock_type2 = _create_mock_type_version_manager()
        mock_get_global_version_managers.return_value = [mock_type1, mock_type2]
        mock_get_all_buckets.return_value = []

        self.assertTrue(len(get_no_buckets_types()) == 2)

    @patch.object(TypeVersionManager, 'get_global_version_managers')
    @patch.object(Bucket, 'get_all')
    def test_get_no_buckets_types_returns_all_types_not_in_buckets(self, mock_get_all_buckets,
                                                                   mock_get_global_version_managers):
        # Arrange
        mock_type1 = _create_mock_type_version_manager()
        mock_type2 = _create_mock_type_version_manager()

        mock_bucket = _create_mock_bucket(types=[mock_type1])

        mock_get_global_version_managers.return_value = [mock_type1, mock_type2]
        mock_get_all_buckets.return_value = [mock_bucket]

        self.assertTrue(len(get_no_buckets_types()) == 1)


def _create_mock_bucket(types=None):
    """Returns a mock bucket

    Args:
        types:

    Returns:

    """
    if types is None:
        types = []
    mock_bucket = Mock(spec=Bucket)
    mock_bucket.label = 'bucket'
    mock_bucket.label = '#000000'
    mock_bucket.types = types
    return mock_bucket


def _create_mock_type(filename="", content="", is_disable=False):
    """Returns a mock type

    Args:
        filename:
        content:
        is_disable:

    Returns:

    """
    mock_type = Mock(spec=Type)
    mock_type.filename = filename
    mock_type.content = content
    mock_type.id = ObjectId()
    mock_type.is_disabled = is_disable
    return mock_type


def _create_mock_type_version_manager(title="", versions=None, user='1'):
    """Returns a mock type version manager

    Args:
        title:
        versions:

    Returns:

    """
    mock_type_version_manager = Mock(spec=TypeVersionManager)
    mock_type_version_manager.title = title
    mock_type_version_manager.id = ObjectId()
    mock_type_version_manager.user = user
    if versions is not None:
        mock_type_version_manager.versions = versions
    else:
        mock_type_version_manager.versions = []
    mock_type_version_manager.disabled_versions = []
    return mock_type_version_manager


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


def _create_type_version_manager(title="", user='1'):
    """Returns a type version manager

    Args:
        title:
        user:

    Returns:

    """
    return TypeVersionManager(
        id=ObjectId(),
        title=title,
        versions=[],
        user=user,
        disabled_versions=[]
    )
