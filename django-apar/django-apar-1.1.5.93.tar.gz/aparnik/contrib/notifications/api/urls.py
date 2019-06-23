from django.conf.urls import url, include

from .views import NotificationListAPIView, NotificationReadAPIView, NotificationDetailAPIView

app_name = 'notifications'

urlpatterns = [
    url(r'^$', NotificationListAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/read/$', NotificationReadAPIView.as_view(), name='read'),
    url(r'^(?P<id>\d+)/$', NotificationDetailAPIView.as_view(), name='detail'),
    url(r'^read/$', NotificationReadAPIView.as_view(), name='reads-all'),
]