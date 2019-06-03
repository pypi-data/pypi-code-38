""" Url router for the Text Area module
"""
from django.conf.urls import url

from core_module_text_area_app.views.views import TextAreaModule

urlpatterns = [
    url(r'module-text-area', TextAreaModule.as_view(), name='core_module_text_area_view'),
]
