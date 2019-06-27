from django.conf.urls import url, include

from .views import TeacherSortAdminAPIView, TeacherAdminListAPIView

app_name = 'teachers'

urlpatterns = [
    url(r'^$', TeacherAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', TeacherSortAdminAPIView.as_view(), name='sort'),
]
