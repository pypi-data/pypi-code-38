""" Authentication tests for Bucket REST API
"""
from django.test import SimpleTestCase
from mock.mock import patch
from rest_framework import status

from core_composer_app.components.bucket.models import Bucket
from core_composer_app.rest.bucket import views as bucket_views
from core_composer_app.rest.bucket.serializers import BucketSerializer
from core_main_app.components.version_manager.models import VersionManager
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock


class TestBucketListGetPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            bucket_views.BucketList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(Bucket, "get_all")
    def test_authenticated_returns_http_200(self, bucket_get_all):
        bucket_get_all.return_value = {}

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            bucket_views.BucketList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(Bucket, "get_all")
    def test_staff_returns_http_200(self, bucket_get_all):
        bucket_get_all.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            bucket_views.BucketList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestBucketListPostPermission(SimpleTestCase):

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            bucket_views.BucketList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_post(
            bucket_views.BucketList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(BucketSerializer, "is_valid")
    @patch.object(BucketSerializer, "save")
    @patch.object(BucketSerializer, "data")
    def test_staff_returns_http_201(self, bucket_serializer_data, bucket_serializer_save,
                                    bucket_serializer_valid):
        bucket_serializer_data.return_value = True
        bucket_serializer_save.return_value = None
        bucket_serializer_valid.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_post(
            bucket_views.BucketList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestBucketDetailGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            bucket_views.BucketDetail.as_view(),
            None,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(Bucket, "get_by_id")
    @patch.object(BucketSerializer, "data")
    def test_authenticated_returns_http_200(self, bucket_get_by_id, bucket_serializer_data):
        bucket_get_by_id.return_value = {}
        bucket_serializer_data.return_value = True

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            bucket_views.BucketDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(Bucket, "get_by_id")
    @patch.object(BucketSerializer, "data")
    def test_staff_returns_http_200(self, bucket_get_by_id, bucket_serializer_data):
        bucket_get_by_id.return_value = {}
        bucket_serializer_data.return_value = True

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            bucket_views.BucketDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestBucketDetailDeletePermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_delete(
            bucket_views.BucketDetail.as_view(),
            None,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_delete(
            bucket_views.BucketDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(Bucket, "get_by_id")
    @patch('core_composer_app.components.bucket.api.delete')
    def test_staff_returns_http_204(self, bucket_get_by_id, bucket_api_delete):
        bucket_get_by_id.return_value = {}
        bucket_api_delete.return_value = None

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_delete(
            bucket_views.BucketDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestBucketDetailPatchPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):

        response = RequestMock.do_request_patch(
            bucket_views.BucketDetail.as_view(),
            None,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_patch(
            bucket_views.BucketDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(Bucket, "get_by_id")
    @patch.object(BucketSerializer, "is_valid")
    @patch.object(BucketSerializer, "save")
    @patch.object(BucketSerializer, "data")
    def test_staff_returns_http_200(self, bucket_serializer_data, bucket_serializer_save,
                                    bucket_serializer_valid, bucket_get_by_id):
        bucket_get_by_id.return_value = {}
        bucket_serializer_data.return_value = True
        bucket_serializer_save.return_value = None
        bucket_serializer_valid.return_value = {}

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_patch(
            bucket_views.BucketDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTypeVersionManagerBucketsPatchPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_patch(
            bucket_views.TypeVersionManagerBuckets.as_view(),
            None,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_returns_http_403(self):
        mock_user = create_mock_user('1')

        response = RequestMock.do_request_patch(
            bucket_views.TypeVersionManagerBuckets.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(Bucket, "get_by_id")
    @patch.object(VersionManager, "get_by_id")
    @patch.object(BucketSerializer, "is_valid")
    @patch.object(BucketSerializer, "save")
    @patch.object(BucketSerializer, "data")
    def test_staff_returns_http_200(self, bucket_serializer_data, bucket_serializer_save,
                                    bucket_serializer_valid, version_manager_get_by_id, bucket_get_by_id):
        bucket_get_by_id.return_value = {}
        version_manager_get_by_id.return_value = {}
        bucket_serializer_data.return_value = True
        bucket_serializer_save.return_value = None
        bucket_serializer_valid.return_value = {}
        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_patch(
            bucket_views.TypeVersionManagerBuckets.as_view(),
            mock_user,
            param={'pk': self.fake_id},
            data=[]
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
