from django.conf.urls import include, url

from aparnik.contrib.province.api.views import CityCreateAPIView, CityDetailAPIView, CityListAPIView

app_name = 'province'

urlpatterns = [
    url(r'^$', CityListAPIView.as_view(), name='list'),
    url(r'^create/$', CityCreateAPIView.as_view(), name='create'),
    url(r'^(?P<id>\d+)/$', CityDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<city_id>\d+)/town/', include('aparnik.contrib.province.api.urls-town', namespace='town-api')),
]