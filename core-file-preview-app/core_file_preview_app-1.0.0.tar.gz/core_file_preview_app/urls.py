""" Url router for the file preview app
"""
from django.conf.urls import url

from core_file_preview_app.views.user.ajax import get_blob_preview

urlpatterns = [
    url(r'^get_blob_preview', get_blob_preview,
        name='core_file_preview_app_get_blob_preview'),
]
