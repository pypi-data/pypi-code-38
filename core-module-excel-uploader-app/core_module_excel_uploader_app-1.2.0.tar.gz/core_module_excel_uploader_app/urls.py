""" Url router for the excel uploader module
"""
from django.conf.urls import url

from core_module_excel_uploader_app.views.views import ExcelUploaderModule

urlpatterns = [
    url(r'module-excel-uploader', ExcelUploaderModule.as_view(), name='core_module_excel_uploader_view'),
]
