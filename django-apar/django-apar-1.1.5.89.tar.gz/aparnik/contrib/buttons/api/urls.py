from django.conf.urls import url, include
from aparnik.contrib.segments.api.views import BaseSegmentListAPIView, BaseSegmentModelListAPIView

app_name = 'buttons'

urlpatterns = [
    url(r'^$', BaseSegmentListAPIView.as_view(), name='list'),
    url(r'^(?P<segment_id>\d+)/$', BaseSegmentModelListAPIView.as_view(), name='list-model-segment'),
]
