from django.conf.urls import url, include

from .views import payment

app_name = 'payments'

urlpatterns = [
    url(r'^(?P<uuid>[0-9a-f-]+)/pay/$', payment, name='payment'),
    # url(r'^(?P<id>\d+)/pay/$', TransactionPayAPIView.as_view(), name='pay'),
    # url(r'^(?P<id>\d+)/$', TransactionDetailAPIView.as_view(), name='detail'),

]