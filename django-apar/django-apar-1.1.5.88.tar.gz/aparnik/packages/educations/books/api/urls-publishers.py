from django.conf.urls import url, include

from .views import PublisherListAPIView, PublisherDetailsAPIView

app_name = 'books'

urlpatterns = [
    url(r'^$', PublisherListAPIView.as_view(), name='list'),
    url(r'^(?P<publisher_id>\d+)/$', PublisherDetailsAPIView.as_view(), name='details'),
]
