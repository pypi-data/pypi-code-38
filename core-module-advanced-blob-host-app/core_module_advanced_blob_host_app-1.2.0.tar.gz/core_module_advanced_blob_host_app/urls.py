""" Url router for the advanced blob host module
"""
from django.conf.urls import url

from core_module_advanced_blob_host_app.views.views import AdvancedBlobHostModule

urlpatterns = [
    url(r'module-advanced-blob-host', AdvancedBlobHostModule.as_view(), name='core_module_advanced_blob_host_view'),
]
