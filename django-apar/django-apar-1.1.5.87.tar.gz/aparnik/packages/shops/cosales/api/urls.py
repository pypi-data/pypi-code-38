from django.conf.urls import url, include
from .views import CoSaleUserListAPIView, CoSaleListAPIView


app_name = 'cosales'

urlpatterns = [
    url(r'^$', CoSaleListAPIView.as_view(), name='list'),
    url(r'^user/$', CoSaleUserListAPIView.as_view(), name='user-list'),
    # url(r'^(?P<id>\d+)/add-address/$', AddOrderAddressAPIView.as_view(), name='add-address'),
]
