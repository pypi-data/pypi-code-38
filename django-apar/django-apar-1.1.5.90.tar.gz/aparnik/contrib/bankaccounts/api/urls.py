from django.conf.urls import url, include

from .views import BankAccountListAPIView, BankAccountSetAPIView, BankAccountUpdateAPIView, BankAccountCreateAPIView, BankNameListAPIView

app_name = 'bankaccounts'

urlpatterns = [
    url(r'^$', BankAccountListAPIView.as_view(), name='list'),
    url(r'^bankname/$', BankNameListAPIView.as_view(), name='bankname-list'),
    url(r'^(?P<model_id>\d+)/set/$', BankAccountSetAPIView.as_view(), name='set'),
    url(r'^(?P<model_id>\d+)/update/$', BankAccountUpdateAPIView.as_view(), name='update'),
    url(r'^create/$', BankAccountCreateAPIView.as_view(), name='create'),
]