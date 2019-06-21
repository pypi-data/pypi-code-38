from django.conf.urls import url, include

from .views import NotifyMeListAPIView, NotifyMeSetAPIView

app_name = 'notifiesme'

urlpatterns = [
    url(r'^$', NotifyMeListAPIView.as_view(), name='list'),
    url(r'^(?P<model_id>\d+)/set/$', NotifyMeSetAPIView.as_view(), name='set'),
    # url(r'^model/(?P<model_id>\d+)/set/$', BookmarkSetAPIView.as_view(), name='set'),

]