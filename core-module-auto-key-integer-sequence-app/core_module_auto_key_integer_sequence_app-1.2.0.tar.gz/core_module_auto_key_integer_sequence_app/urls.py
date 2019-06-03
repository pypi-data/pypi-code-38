"""Url routing
"""
from django.conf.urls import url

from core_module_auto_key_integer_sequence_app.views import AutoKeyIntModule

urlpatterns = [
    url(r'module-auto-key-int-sequence', AutoKeyIntModule.as_view(), name='core_auto_key_int_sequence_view'),
]
