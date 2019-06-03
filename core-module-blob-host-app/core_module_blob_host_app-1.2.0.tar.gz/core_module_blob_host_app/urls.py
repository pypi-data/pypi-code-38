""" Url router for the blob host module
"""
from django.conf.urls import url
from core_module_blob_host_app.views.views import BlobHostModule

urlpatterns = [
    url(r'module-blob-host', BlobHostModule.as_view(), name='core_module_blob_host_view'),
]
