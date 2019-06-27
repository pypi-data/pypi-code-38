from django.conf.urls import url

from aparnik.contrib.province.api.views import TownCreateAPIView, TownDetailAPIView, TownListAPIView

app_name = 'province'

urlpatterns = [
    url(r'^$', TownListAPIView.as_view(), name='list'),
    url(r'^create/$', TownCreateAPIView.as_view(), name='create'),
    url(r'^(?P<id>\d+)/$', TownDetailAPIView.as_view(), name='detail')
]