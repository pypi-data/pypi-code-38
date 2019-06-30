from django.conf.urls import url, include

from .views import OrderSortAdminAPIView, OrderAdminListAPIView

app_name = 'orders'

urlpatterns = [
    url(r'^$', OrderAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', OrderSortAdminAPIView.as_view(), name='sort'),
]
