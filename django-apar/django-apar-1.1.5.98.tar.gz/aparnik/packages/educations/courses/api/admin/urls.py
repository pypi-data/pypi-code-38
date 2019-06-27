from django.conf.urls import url, include

from .views import CourseSortAdminAPIView, CourseAdminListAPIView

app_name = 'courses'

urlpatterns = [
    url(r'^$', CourseAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', CourseSortAdminAPIView.as_view(), name='sort'),
]
