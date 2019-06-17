from django.conf.urls import url, include

from .views import CourseListAPIView, CourseDetailAPIView, CourseUserListAPIView, CourseCreateAPIView

app_name = 'courses'

urlpatterns = [
    url(r'^$', CourseListAPIView.as_view(), name='list'),
    url(r'^user/$', CourseUserListAPIView.as_view(), name='user'),
    url(r'^(?P<course_id>\d+)/$', CourseListAPIView.as_view(), name='detail'),
    # url(r'^(?P<course_id>\d+)/step/', include('courses.api.urls-steps', namespace='step')),
    # url(r'^(?P<course_id>\d+)/step/', include('courses.api.urls-steps', namespace='step')),
    url(r'^(?P<course_id>\d+)/file/', include('aparnik.packages.educations.courses.api.urls-files', namespace='files')),
    url(r'^create/$', CourseCreateAPIView.as_view(), name='create'),
]