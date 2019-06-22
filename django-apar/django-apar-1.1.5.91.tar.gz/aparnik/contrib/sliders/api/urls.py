from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token

from .views import SliderDetailAPIView, SliderListAPIView

app_name = 'sliders'

urlpatterns = [
    url(r'^$', SliderListAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', SliderDetailAPIView.as_view(), name='detail'),

]