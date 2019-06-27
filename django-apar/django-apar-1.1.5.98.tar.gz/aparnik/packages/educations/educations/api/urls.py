from django.conf.urls import url

from .views import BaseEducationListAPIView, EducationCreateAPIView, \
    InstituteListAPIView, FieldSubjectListAPIView, EducationUpdateAPIView, DegreeListAPIView

app_name = 'educations'

urlpatterns = [
    url(r'^$', BaseEducationListAPIView.as_view(), name='list'),
    url(r'^create/$', EducationCreateAPIView.as_view(), name='create'),
    url(r'^(?P<education_id>[\w-]+)/update', EducationUpdateAPIView.as_view(), name='update'),
    url(r'^institutes/$', InstituteListAPIView.as_view(), name='institude-list'),
    url(r'^field-subjects/$', FieldSubjectListAPIView.as_view(), name='field-subject-list'),
    url(r'^degree/$', DegreeListAPIView.as_view(), name='degree-list'),
]
