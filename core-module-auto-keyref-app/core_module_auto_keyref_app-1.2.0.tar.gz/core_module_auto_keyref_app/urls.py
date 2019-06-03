"""Url routing
"""
from django.conf.urls import url

from core_module_auto_keyref_app.views import AutoKeyRefModule
from core_module_auto_keyref_app.ajax import get_updated_keys

urlpatterns = [
    url(r'module-auto-keyref', AutoKeyRefModule.as_view(), name='core_auto_keyref_view'),
    url(r'get-updated-keys', get_updated_keys, name='core_module_auto_keyref_app_get_updated_keys')
]
