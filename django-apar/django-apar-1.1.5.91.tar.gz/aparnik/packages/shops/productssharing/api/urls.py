from django.conf.urls import url, include

from .views import ProductSharingListAPIView, ProductSharingSetAPIView

app_name = 'productsharing'

urlpatterns = [
    url(r'^$', ProductSharingListAPIView.as_view(), name='list'),
    url(r'^(?P<product_id>\d+)/users/$', ProductSharingListAPIView.as_view(), name='product-user-share-list'),
    url(r'^(?P<product_id>\d+)/set/$', ProductSharingSetAPIView.as_view(), name='product-share-set'),
    # url(r'^model/(?P<model_id>\d+)/set/$', BookmarkSetAPIView.as_view(), name='set'),

]