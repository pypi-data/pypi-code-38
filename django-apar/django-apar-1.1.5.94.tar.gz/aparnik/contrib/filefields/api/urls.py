from django.conf.urls import url, include

from .views import SignS3, FileFieldCreateAPIView, FileFieldListAPIView

app_name = 'filefields'

urlpatterns = [
    url(r'^filefileds-list/', FileFieldListAPIView.as_view(), name='list'),
    url(r'^sign-s3/', SignS3.as_view(), name='s3-sign'),
    url(r'^create/', FileFieldCreateAPIView.as_view(), name='create'),
]