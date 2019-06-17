from django.conf.urls import url, include

from .views import PaymentPayListAPIView, PaymentPayAPIView, PayAPIView, PaymentPayCancelAPIView


app_name = 'payments'

urlpatterns = [
    url(r'^$', PaymentPayListAPIView.as_view(), name='list'),
    url(r'^(?P<uuid>[0-9a-f-]+)/pay/$', PaymentPayAPIView.as_view(), name='payment'),
    url(r'^(?P<uuid>[0-9a-f-]+)/cancel/$', PaymentPayCancelAPIView.as_view(), name='cancel'),
]