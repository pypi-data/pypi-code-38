from django.conf.urls import url, include

from .views import ProductSortAdminAPIView, ProductAdminListAPIView

app_name = 'products'

urlpatterns = [
    url(r'^$', ProductAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', ProductSortAdminAPIView.as_view(), name='sort'),
]
