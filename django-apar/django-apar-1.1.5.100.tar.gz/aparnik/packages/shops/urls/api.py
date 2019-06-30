from django.conf.urls import url, include

app_name = 'shops'

urlpatterns = [
    url(r'^products/', include('aparnik.packages.shops.products.api.urls', namespace='products')),
    url(r'^payments/', include('aparnik.packages.shops.payments.api.urls', namespace='payments')),
    url(r'^orders/', include('aparnik.packages.shops.orders.api.urls', namespace='orders')),
    url(r'^files/', include('aparnik.packages.shops.files.api.urls', namespace='files')),
    url(r'^productssharing/', include('aparnik.packages.shops.productssharing.api.urls', namespace='productssharing')),
    url(r'^vouchers/', include('aparnik.packages.shops.vouchers.api.urls', namespace='vouchers')),
    url(r'^subscriptions/', include('aparnik.packages.shops.subscriptions.api.urls', namespace='subscriptions')),
    url(r'^cosales/', include('aparnik.packages.shops.cosales.api.urls', namespace='cosales')),
    url(r'^coupons/', include('aparnik.packages.shops.coupons.api.urls', namespace='coupons')),
]
