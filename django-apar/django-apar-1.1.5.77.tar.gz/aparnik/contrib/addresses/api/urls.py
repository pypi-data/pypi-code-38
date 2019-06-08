from django.conf.urls import url, include

from .views import AddressListAPIView, AddressSetAPIView, AddressCreateAPIView

urlpatterns = [
    url(r'^$', AddressListAPIView.as_view(), name='list'),
    url(r'^(?P<model_id>\d+)/set/$', AddressSetAPIView.as_view(), name='set'),
    url(r'^create/$', AddressCreateAPIView.as_view(), name='create'),
]