from django.conf.urls import url, include

from .views import TeacherListAPIView, TeacherModelsListAPIView

app_name = 'teachers'

urlpatterns = [
    url(r'^$', TeacherListAPIView.as_view(), name='list'),
    url(r'^admin/', include('aparnik.packages.educations.teachers.api.admin.urls', namespace='admin')),
    url(r'^(?P<teacher_id>\d+)/models/$', TeacherModelsListAPIView.as_view(), name='models-list'),
]
