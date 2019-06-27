from django.conf.urls import url, include

from .views import OrderListAPIView, OrderDetailAPIView, AddProductOrderAPIView, AddOrderAddressAPIView, \
    ChargeWalletAPIView, RemoveProductOrderAPIView, AddProductOrderByWebsitesAPIView
from aparnik.packages.shops.payments.api.views import PayAPIView
from aparnik.packages.shops.coupons.api.views import CouponAPIView


app_name = 'orders'

urlpatterns = [
    url(r'^$', OrderListAPIView.as_view(), name='list'),
    url(r'^admin/', include('aparnik.packages.shops.orders.api.admin.urls', namespace='admin')),
    url(r'^wallet/charge/$', ChargeWalletAPIView.as_view(), name='charge-wallet'),
    url(r'^add/$', AddProductOrderAPIView.as_view(), name='add'),
    url(r'^websites/pay/$', AddProductOrderByWebsitesAPIView.as_view(), name='add-pay-by-websites'),
    url(r'^(?P<id>\d+)/add-address/$', AddOrderAddressAPIView.as_view(), name='add-address'),
    url(r'^(?P<id>\d+)/add-item/$', AddProductOrderAPIView.as_view(), name='add-item'),
    url(r'^(?P<id>\d+)/remove-item/(?P<item_id>\d+)/$', RemoveProductOrderAPIView.as_view(), name='remove-item'),
    url(r'^(?P<id>\d+)/$', OrderDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/request-pay/$', PayAPIView.as_view(), name='request-pay'),
    url(r'^(?P<id>\d+)/coupon/$', CouponAPIView.as_view(), name='coupon'),
]