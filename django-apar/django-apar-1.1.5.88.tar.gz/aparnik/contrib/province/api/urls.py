from django.conf.urls import include, url

from aparnik.contrib.province.api.views import ProvinceListAPIView, ProvinceCreateAPIView, ProvinceDetailAPIView

app_name = 'province'

urlpatterns = [
    url(r'^$', ProvinceListAPIView.as_view(), name='list'),
    url(r'^create/$', ProvinceCreateAPIView.as_view(), name='create'),
    url(r'^(?P<id>\d+)/$', ProvinceDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<province_id>\d+)/city/', include('aparnik.contrib.province.api.urls-city', namespace='city-api')),
    url(r'^(?P<province_id>\d+)/shahrak/', include('aparnik.contrib.province.api.urls-shahrak', namespace='shahrak-api')),
]