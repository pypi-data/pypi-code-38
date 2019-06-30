from django.conf.urls import url, include


app_name='shops'

urlpatterns = [
    url(r'^payments/', include('aparnik.packages.shops.payments.urls', namespace='payments')),
    url(r'^orders/', include('aparnik.packages.shops.orders.urls', namespace='orders')),
    url(r'^zarinpals/', include('aparnik.packages.shops.zarinpals.urls', namespace='zarinpals')),
]
