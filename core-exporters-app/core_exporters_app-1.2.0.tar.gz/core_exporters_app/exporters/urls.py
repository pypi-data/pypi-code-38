""" Exporters urls
"""
from django.conf.urls import url, include

urlpatterns = [
    url('', include('core_exporters_app.exporters.json_exporter.urls')),
    url('', include('core_exporters_app.exporters.xml.urls')),
    url('', include('core_exporters_app.exporters.blob.urls')),
]
