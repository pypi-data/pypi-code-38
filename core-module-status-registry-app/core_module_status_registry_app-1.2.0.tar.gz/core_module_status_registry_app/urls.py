""" Url router for the Status registry module
"""
from django.conf.urls import url
from core_module_status_registry_app.views.views import StatusRegistryModule

urlpatterns = [
    url(r'module-status-registry', StatusRegistryModule.as_view(), name='core_module_status_registry_view'),
]
