from django.conf.urls import url, include

from .views import TeacherListAPIView, TeacherModelsListAPIView

urlpatterns = [
    url(r'^$', TeacherListAPIView.as_view(), name='list'),
    url(r'^(?P<teacher_id>\d+)/models/$', TeacherModelsListAPIView.as_view(), name='models-list'),
]
