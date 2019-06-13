from .views import DocumentFileView, BulkDocumentFileView
from django.urls import re_path


urlpatterns = [
  re_path(r'^(?P<slug>[\w-]+)/(?P<object_id>[^/.]+)/$', DocumentFileView.as_view(), name='print'),
  re_path(r'^(?P<slug>[\w-]+)/$', BulkDocumentFileView.as_view(), name='print'),
]
