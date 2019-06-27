from django.conf.urls import url, include
from .views import FileListAPIView, FileDownloadRequestAPIView

app_name = 'files'

urlpatterns = [
    url(r'^$', FileListAPIView.as_view(), name='list'),
    # url(r'^(?P<file_id>\d+)/$', FileDetailAPIView.as_view(), name='details'),
    # url(r'^(?P<course_id>\d+)/$', BaseFileFileListAPIView.as_view(), name='list-file'),
    # url(r'^$', BaseFileLibraryListAPIView.as_view(), name='list-library'),

    url(r'^(?P<file_id>\d+)/download-request/$', FileDownloadRequestAPIView.as_view(), name='download-request'),
]
