""" Url router for the remote blob host module
"""
from django.conf.urls import url

from core_module_remote_blob_host_app.views.views import RemoteBlobHostModule

urlpatterns = [
    url(r'module-remote-blob-host', RemoteBlobHostModule.as_view(), name='core_module_remote_blob_host_view'),
]
