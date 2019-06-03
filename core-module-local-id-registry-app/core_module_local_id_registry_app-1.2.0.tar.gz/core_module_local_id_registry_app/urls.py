""" Url router for the local id registry module
"""
from django.conf.urls import url
from core_module_local_id_registry_app.views.views import LocalIdRegistryModule

urlpatterns = [
    url(r'module-local-id-registry', LocalIdRegistryModule.as_view(), name='core_module_local_id_registry_view'),
]
