from django.conf.urls import url, include

from .views import ProductSortAPIView, ProductListAPIView

app_name = 'products'

urlpatterns = [
    url(r'^$', ProductListAPIView.as_view(), name='list'),
    url(r'^admin/', include('aparnik.packages.shops.products.api.admin.urls', namespace='admin')),
    url(r'^sort/$', ProductSortAPIView.as_view(), name='sort'),
]
