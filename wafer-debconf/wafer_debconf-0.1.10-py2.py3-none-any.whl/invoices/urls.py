from django.conf.urls import url

from invoices.views import InvoiceCancel, InvoiceCombine, InvoiceDisplay

app_name = 'invoices'
urlpatterns = [
    url(r'^combine/$', InvoiceCombine.as_view(), name='combine'),
    url(r'^(?P<reference_number>[^/]+)/$', InvoiceDisplay.as_view(),
        name='display'),
    url(r'^(?P<reference_number>[^/]+)/cancel/$', InvoiceCancel.as_view(),
        name='cancel'),
]
