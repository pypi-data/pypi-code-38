from django.conf.urls import url, include

from .views import CourseFileListAPIView, CourseFileCreateAPIView

urlpatterns = [
    url(r'^$', CourseFileListAPIView.as_view(), name='list'),
    url(r'^create/$', CourseFileCreateAPIView.as_view(), name='create'),
    # url(r'^(?P<file_id>\d+)/download-request/$', FileDownloadRequestAPIView.as_view(), name='download-request'),
    # url(r'^preview/$', FileListAPIView.as_view(), name='preview-list'),

    # url(r'^(?P<file_id>\d+)/$', FileListAPIView.as_view(), name='detail'),
    # url(r'^(?P<id>\d+)/file/', include('courses.api.urls-files', namespace='file')),
    # url(r'^(?P<id>\d+)/order/$', CourseOrderAPIView.as_view(), name='order'),
]