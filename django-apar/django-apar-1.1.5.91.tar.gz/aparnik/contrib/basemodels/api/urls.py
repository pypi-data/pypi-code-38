from django.conf.urls import url
from .views import BaseModelDetailAPIView, BaseModelListAPIView, TagDetailsAPIView, ShareAPIView

app_name = 'basemodels'

urlpatterns = [
    url(r'^$', BaseModelListAPIView.as_view(), name='list'),
    url(r'^(?P<model_id>\d+)/$', BaseModelDetailAPIView.as_view(), name='details'),
    url(r'^tags/(?P<model_id>\d+)/$', TagDetailsAPIView.as_view(), name='tags-details'),
    url(r'^(?P<model_id>\d+)/share-content/$', ShareAPIView.as_view(), name='share-content'),
]
