""" Authentication tests for Exporters REST API
"""
from django.test import SimpleTestCase
from mock.mock import patch
from rest_framework import status

import core_exporters_app.components.exported_compressed_file.api as exported_compressed_file_api
import core_exporters_app.components.exporter.api as exporter_api
import core_main_app.components.data.api as data_api
from core_exporters_app.components.exported_compressed_file.models import ExportedCompressedFile
from core_exporters_app.exporters.exporter import AbstractExporter
from core_exporters_app.rest.exporters import views as exporters_api_views
from core_exporters_app.rest.exporters.serializers import ExporterSerializer, ExporterToZipSerializer
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock


class TestExporterListGetPermissions(SimpleTestCase):
    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            exporters_api_views.ExporterList.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(exporter_api, "get_all")
    @patch.object(ExporterSerializer, "data")
    def test_authenticated_returns_http_200(self, mock_exporter_serializer_data, mock_exporter_get_all):
        mock_user = create_mock_user("1")

        response = RequestMock.do_request_get(
            exporters_api_views.ExporterList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(exporter_api, "get_all")
    @patch.object(ExporterSerializer, "data")
    def test_staff_returns_http_200(self, mock_exporter_serializer_data, mock_exporter_get_all):
        mock_user = create_mock_user("1", is_staff=True)

        response = RequestMock.do_request_get(
            exporters_api_views.ExporterList.as_view(),
            mock_user
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestExporterDetailGetPermissions(SimpleTestCase):
    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            exporters_api_views.ExporterDetail.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(exporter_api, "get_by_id")
    @patch.object(ExporterSerializer, "data")
    def test_authenticated_returns_http_200(self, mock_exporter_serializer_data, mock_exporter_get_by_id):
        mock_user = create_mock_user("1")

        response = RequestMock.do_request_get(
            exporters_api_views.ExporterDetail.as_view(),
            mock_user,
            param={"pk": "0"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(exporter_api, "get_by_id")
    @patch.object(ExporterSerializer, "data")
    def test_staff_returns_http_200(self, mock_exporter_serializer_data, mock_exporter_get_by_id):
        mock_user = create_mock_user("1", is_staff=True)

        response = RequestMock.do_request_get(
            exporters_api_views.ExporterDetail.as_view(),
            mock_user,
            param={"pk": "0"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestExportToZipPostPermissions(SimpleTestCase):
    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_post(
            exporters_api_views.ExportToZip.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(ExporterToZipSerializer, "data")
    @patch.object(ExporterToZipSerializer, "is_valid")
    @patch.object(exported_compressed_file_api, "upsert")
    @patch.object(data_api, "get_by_id_list")
    @patch.object(AbstractExporter, "export")
    def test_authenticated_returns_http_200(self,
                                            mock_abstract_exporter_export,
                                            mock_data_get_by_id_list,
                                            mock_exported_compressed_file_upsert,
                                            mock_exporter_exporter_is_valid,
                                            mock_exporter_exporter_data):
        mock_data_get_by_id_list.return_value = None
        mock_user = create_mock_user("1")

        response = RequestMock.do_request_post(
            exporters_api_views.ExportToZip.as_view(),
            mock_user,
            data={
                "data_id_list": "0",
                "exporter_id_list": ""
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(ExporterToZipSerializer, "data")
    @patch.object(ExporterToZipSerializer, "is_valid")
    @patch.object(exported_compressed_file_api, "upsert")
    @patch.object(data_api, "get_by_id_list")
    @patch.object(AbstractExporter, "export")
    def test_staff_returns_http_200(self,
                                    mock_abstract_exporter_export,
                                    mock_data_get_by_id_list,
                                    mock_exported_compressed_file_upsert,
                                    mock_exporter_exporter_is_valid,
                                    mock_exporter_exporter_data):
        mock_data_get_by_id_list.return_value = None
        mock_user = create_mock_user("1", is_staff=True)

        response = RequestMock.do_request_post(
            exporters_api_views.ExportToZip.as_view(),
            mock_user,
            data={
                "data_id_list": "0",
                "exporter_id_list": ""
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestExporterDownloadGetPermissions(SimpleTestCase):
    def test_anonymous_returns_http_403(self):
        response = RequestMock.do_request_get(
            exporters_api_views.ExporterDownload.as_view(),
            None
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(exported_compressed_file_api, "get_by_id")
    def test_authenticated_returns_http_200(self, mock_exported_compressed_file_get_by_id):
        mock_exported_compressed_file_get_by_id.return_value = ExportedCompressedFile(
            is_ready=True,
            file=None,
            file_name=""
        )
        mock_user = create_mock_user("1")

        response = RequestMock.do_request_get(
            exporters_api_views.ExporterDownload.as_view(),
            mock_user,
            param={"pk": "0"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(exported_compressed_file_api, "get_by_id")
    def test_staff_returns_http_200(self, mock_exported_compressed_file_get_by_id):
        mock_exported_compressed_file_get_by_id.return_value = ExportedCompressedFile(
            is_ready=True,
            file=None,
            file_name=""
        )
        mock_user = create_mock_user("1", is_staff=True)

        response = RequestMock.do_request_get(
            exporters_api_views.ExporterDownload.as_view(),
            mock_user,
            param={"pk": "0"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
