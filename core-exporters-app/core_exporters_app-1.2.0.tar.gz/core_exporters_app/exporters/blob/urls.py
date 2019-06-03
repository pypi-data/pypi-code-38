""" Json exporter url
"""
from django.conf.urls import url

from core_exporters_app.exporters.blob.models import BlobExporter

urlpatterns = [
   url('', BlobExporter, {'name': 'BLOB', 'enable_by_default': True}),
]
