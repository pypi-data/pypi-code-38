""" Url router for the REST API
"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from core_exporters_app.rest.exporters import views as exporters_views
from core_exporters_app.rest.exporters.xsl import views as xsl_views

urlpatterns = [
    url(r'^exporter/export/$', exporters_views.ExportToZip.as_view(),
        name='core_exporters_app_rest_exporter_export'),

    url(r'^exporter/xsl/$', xsl_views.ExporterXslList.as_view(),
        name='core_exporters_app_rest_exporter_xsl'),

    url(r'^exporter/xsl/(?P<pk>\w+)/$', xsl_views.ExporterXslDetail.as_view(),
        name='core_exporters_app_rest_exporter_xsl_detail'),

    url(r'^exporter/$', exporters_views.ExporterList.as_view(),
        name='core_exporters_app_rest_exporter'),

    url(r'^exporter/(?P<pk>\w+)/$', exporters_views.ExporterDetail.as_view(),
        name='core_exporters_app_rest_exporter_detail'),

    url(r'^exporter/export/download/(?P<pk>\w+)/$', exporters_views.ExporterDownload.as_view(),
        name='core_exporters_app_rest_exporter_export_download'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
