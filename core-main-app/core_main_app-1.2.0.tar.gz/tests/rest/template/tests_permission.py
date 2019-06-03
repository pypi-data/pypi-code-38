""" Authentication tests for Template REST API
"""
from django.test import SimpleTestCase
from mock.mock import patch
from rest_framework import status

from core_main_app.components.template.models import Template
from core_main_app.rest.template import views as template_views
from core_main_app.rest.template.serializers import TemplateSerializer
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock


class TestTemplateDetailGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    @patch.object(Template, "get_by_id")
    @patch.object(TemplateSerializer, "data")
    def test_anonymous_returns_http_200(self, template_serializer_data, template_get_by_id):
        template_get_by_id.return_value = {}
        template_serializer_data.return_value = True

        response = RequestMock.do_request_get(
            template_views.TemplateDetail.as_view(),
            None,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(Template, "get_by_id")
    @patch.object(TemplateSerializer, "data")
    def test_authenticated_returns_http_200(self, template_serializer_data, template_get_by_id):
        template_get_by_id.return_value = {}
        template_serializer_data.return_value = True

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            template_views.TemplateDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(Template, "get_by_id")
    @patch.object(TemplateSerializer, "data")
    def test_staff_returns_http_200(self, template_serializer_data, template_get_by_id):
        template_get_by_id.return_value = {}
        template_serializer_data.return_value = True

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            template_views.TemplateDetail.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTemplateDownloadGetPermission(SimpleTestCase):

    def setUp(self):
        self.fake_id = '507f1f77bcf86cd799439011'

    @patch.object(Template, "get_by_id")
    def test_anonymous_returns_http_200(self, template_get_by_id):
        template_get_by_id.return_value = Template(content='test', filename='test.txt')

        response = RequestMock.do_request_get(
            template_views.TemplateDownload.as_view(),
            None,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(Template, "get_by_id")
    def test_authenticated_returns_http_200(self, template_get_by_id):
        template_get_by_id.return_value = Template(content='test', filename='test.txt')

        mock_user = create_mock_user('1')

        response = RequestMock.do_request_get(
            template_views.TemplateDownload.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(Template, "get_by_id")
    def test_staff_returns_http_200(self, template_get_by_id):
        template_get_by_id.return_value = Template(content='test', filename='test.txt')

        mock_user = create_mock_user('1', is_staff=True)

        response = RequestMock.do_request_get(
            template_views.TemplateDownload.as_view(),
            mock_user,
            param={'pk': self.fake_id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
