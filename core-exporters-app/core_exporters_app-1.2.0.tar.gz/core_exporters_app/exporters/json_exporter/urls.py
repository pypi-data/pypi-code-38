""" Json exporter url
"""
from django.conf.urls import url

from core_exporters_app.exporters.json_exporter.models import JsonExporter

urlpatterns = [
   url('', JsonExporter, {'name': 'JSON', 'enable_by_default': True}),
]
