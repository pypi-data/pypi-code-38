""" Url router for the exporters application
"""
from django.conf.urls import url, include
from core_exporters_app.views.user import ajax as user_ajax, views as user_views


urlpatterns = [
    url(r'^rest/', include('core_exporters_app.rest.urls')),
    url(r'^selection', user_ajax.exporters_selection,
        name='core_exporters_app_exporters_selection'),
    url(r'^open-form', user_ajax.open_form,
        name='core_exporters_app_exporters_open_form'),
    url(r'^download', user_views.download_exported_compressed_file,
        name='core_exporters_app_exporters_download'),
    url(r'^status-file', user_ajax.check_download_status,
        name='core_exporters_app_exporters_check_download'),
    url(r'^', include('core_exporters_app.exporters.urls')),
]
