""" Url router for the raw xml module
"""
from django.conf.urls import url

from core_module_raw_xml_app.views.views import RawXmlModule

urlpatterns = [
    url(r'module-raw-xml', RawXmlModule.as_view(), name='core_module_raw_xml_view'),
]
