from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token

from .views import SupportListAPIView, SupportDetailAPIView

app_name = 'supports'

urlpatterns = [
    url(r'^$', SupportListAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', SupportDetailAPIView.as_view(), name='detail'),

]