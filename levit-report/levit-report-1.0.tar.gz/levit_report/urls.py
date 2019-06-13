from .views import DocumentFileView, BulkDocumentFileView

try:
    # Django 2.x
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path


urlpatterns = [
  re_path(r'^(?P<slug>[\w-]+)/(?P<object_id>[^/.]+)/$', DocumentFileView.as_view(), name='print'),
  re_path(r'^(?P<slug>[\w-]+)/$', BulkDocumentFileView.as_view(), name='print'),
]
