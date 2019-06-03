"""Bucket test cases
"""
from unittest.case import TestCase
from bson.objectid import ObjectId
from mock.mock import Mock, patch
from core_main_app.commons import exceptions

from core_composer_app.components.bucket.models import Bucket
from core_composer_app.components.bucket import api as bucket_api
from core_composer_app.components.type_version_manager.models import TypeVersionManager


class TestBucketGetById(TestCase):
    @patch.object(Bucket, 'get_by_id')
    def test_bucket_get_by_id_returns_bucket(self, mock_get_by_id):
        # Arrange
        mock_bucket = _create_mock_bucket()

        mock_get_by_id.return_value = mock_bucket

        # Act
        result = bucket_api.get_by_id(mock_bucket.id)

        # Assert
        self.assertIsInstance(result, Bucket)

    @patch.object(Bucket, 'get_by_id')
    def test_bucket_get_by_id_raises_exception_if_object_does_not_exist(self, mock_get_by_id):
        # Arrange
        mock_absent_id = ObjectId()
        mock_get_by_id.side_effect = exceptions.DoesNotExist('')

        # Act + Assert
        with self.assertRaises(exceptions.DoesNotExist):
            bucket_api.get_by_id(mock_absent_id)


class TestBucketUpsert(TestCase):
    @patch.object(Bucket, 'get_colors')
    @patch.object(Bucket, 'save')
    def test_upsert_bucket_returns_bucket(self, mock_save, mock_get_colors):
        bucket = _create_bucket()

        mock_save.return_value = bucket
        mock_get_colors.return_value = []
        result = bucket_api.upsert(bucket)
        self.assertIsInstance(result, Bucket)


class TestBucketGetAll(TestCase):
    @patch.object(Bucket, 'get_all')
    def test_get_all_buckets_returns_buckets(self, mock_get_all):
        # Arrange
        mock_bucket1 = _create_mock_bucket()
        mock_bucket2 = _create_mock_bucket()

        mock_get_all.return_value = [mock_bucket1, mock_bucket2]

        # Act
        result = bucket_api.get_all()

        # Assert
        self.assertTrue(all(isinstance(item, Bucket) for item in result))


class TestAddTypeToBuckets(TestCase):
    @patch.object(Bucket, 'get_by_id')
    @patch.object(Bucket, 'get_colors')
    @patch.object(Bucket, 'save')
    def test_add_type_to_buckets_adds_one_to_list(self, mock_save, mock_get_colors, mock_get_by_id):
        bucket = _create_bucket()
        mock_save.return_value = bucket
        mock_get_by_id.return_value = bucket
        mock_get_colors.return_value = []

        mock_version_manager = _create_mock_type_version_manager()

        self.assertTrue(len(bucket.types) == 0)
        bucket_api.add_type_to_buckets(mock_version_manager, [bucket.id])
        self.assertTrue(len(bucket.types) == 1)

    @patch.object(Bucket, 'get_by_id')
    @patch.object(Bucket, 'get_colors')
    @patch.object(Bucket, 'save')
    def test_add_no_type_to_buckets_does_not_update_bucket(self, mock_save, mock_get_colors, mock_get_by_id):
        bucket = _create_bucket()
        mock_save.return_value = bucket
        mock_get_by_id.return_value = bucket
        mock_get_colors.return_value = []

        mock_version_manager = _create_mock_type_version_manager()

        self.assertTrue(len(bucket.types) == 0)
        bucket_api.add_type_to_buckets(mock_version_manager, [])
        self.assertTrue(len(bucket.types) == 0)

    @patch.object(Bucket, 'get_by_id')
    @patch.object(Bucket, 'get_colors')
    @patch.object(Bucket, 'save')
    def test_add_type_to_buckets_raises_exception_if_bucket_id_not_found(self, mock_save, mock_get_colors,
                                                                         mock_get_by_id):

        mock_get_by_id.side_effect = exceptions.DoesNotExist
        mock_get_colors.return_value = []

        mock_version_manager = _create_mock_type_version_manager()

        with self.assertRaises(exceptions.ApiError):
            bucket_api.add_type_to_buckets(mock_version_manager, [ObjectId()])


class TestRemoveTypeFromBuckets(TestCase):
    @patch.object(Bucket, 'get_all')
    @patch.object(Bucket, 'get_by_id')
    @patch.object(Bucket, 'get_colors')
    @patch.object(Bucket, 'save')
    def test_remove_type_from_buckets_substracts_one_to_list(self, mock_save, mock_get_colors,
                                                             mock_get_by_id, mock_get_all):
        bucket = _create_bucket()
        mock_version_manager = _create_mock_type_version_manager()

        bucket.types = [mock_version_manager]
        mock_get_all.return_value = [bucket]

        mock_save.return_value = bucket
        mock_get_by_id.return_value = bucket
        mock_get_colors.return_value = []

        self.assertTrue(len(bucket.types) == 1)
        bucket_api.remove_type_from_buckets(mock_version_manager)
        self.assertTrue(len(bucket.types) == 0)

    @patch.object(Bucket, 'get_all')
    @patch.object(Bucket, 'get_by_id')
    @patch.object(Bucket, 'get_colors')
    @patch.object(Bucket, 'save')
    def test_removes_absent_type_from_buckets_does_not_update_bucket(self, mock_save, mock_get_colors,
                                                                     mock_get_by_id, mock_get_all):
        bucket = _create_bucket()
        mock_version_manager = _create_mock_type_version_manager()
        mock_absent_version_manager = _create_mock_type_version_manager()

        bucket.types = [mock_version_manager]
        mock_get_all.return_value = [bucket]

        mock_save.return_value = bucket
        mock_get_by_id.return_value = bucket
        mock_get_colors.return_value = []

        self.assertTrue(len(bucket.types) == 1)
        bucket_api.remove_type_from_buckets(mock_absent_version_manager)
        self.assertTrue(len(bucket.types) == 1)


def _create_mock_bucket():
    """Returns a mock bucket

    Args:

    Returns:

    """
    mock_bucket = Mock(spec=Bucket)
    mock_bucket.label = 'bucket'
    mock_bucket.color = '#000000'
    mock_bucket.types = []
    mock_bucket.id = ObjectId()
    return mock_bucket


def _create_bucket():
    """Returns a bucket

    Args:

    Returns:

    """
    return Bucket(
        id=ObjectId(),
        label="bucket",
        color="#000000",
        types=[]
    )


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
