try:
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode


def payment_url(gateway, order_id, amount, currency=None, email='', lang=None):
    from .models import Gateway

    if not isinstance(gateway, Gateway):
        try:
            gateway = Gateway.objects.get(slug=gateway)
        except Gateway.DoesNotExist:
            return None

    if not currency:
        currency = gateway.default_currency

    return 'https://www.pays.cz/paymentorder?' + urlencode({
        'Merchant': gateway.merchant_id,
        'Shop': gateway.shop_id,
        'MerchantOrderNumber': order_id,
        'Amount': int(amount * Gateway.CURRENCY_BASE_UNITS.get(currency, 100)),
        'Currency': currency,
        'Lang': lang or gateway.default_lang,
        'Email': email,
    })
