from django.conf.urls import url

from aparnik.contrib.province.api.views import ShahrakCreateAPIView, ShahrakDetailAPIView, ShahrakListAPIView

app_name = 'province'

urlpatterns = [
    url(r'^$', ShahrakListAPIView.as_view(), name='list'),
    url(r'^create/$', ShahrakCreateAPIView.as_view(), name='create'),
    url(r'^(?P<id>\d+)/$', ShahrakDetailAPIView.as_view(), name='detail')
]