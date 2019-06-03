from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from votebase.core.payments.views import PricingView, BuyStandardView, \
    BuyPremiumView, CheckoutSuccess, CheckoutCancel, CheckoutError, \
    CheckoutNotify


urlpatterns = patterns(
    '',
    url(_(r'^pricing/$'), PricingView.as_view(), name='pricing'),
    url(_(r'^buy-standard/$'), BuyStandardView.as_view(), name='payments_buy_standard'),
    url(_(r'^buy-premium/$'), BuyPremiumView.as_view(), name='payments_buy_premium'),
    url(_(r'^success/$'), CheckoutSuccess.as_view(), name='payments_success'),
    url(_(r'^cancel/$'), CheckoutCancel.as_view(), name='payments_cancel'),
    url(_(r'^error/$'), CheckoutError.as_view(), name='payments_error'),
    url(_(r'^notify/$'), CheckoutNotify.as_view(), name='payments_notify'),
)
