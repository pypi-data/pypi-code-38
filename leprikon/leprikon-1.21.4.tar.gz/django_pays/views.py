import hmac

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Gateway, Payment


def confirm(request, slug):
    gateway = get_object_or_404(Gateway, slug=slug)
    response = HttpResponse()
    response.status_code = 202

    try:
        msg = (
            '{PaymentOrderID[0]}{MerchantOrderNumber[0]}{PaymentOrderStatusID[0]}'
            '{CurrencyID[0]}{Amount[0]}{CurrencyBaseUnits[0]}'.format(**request.GET)
        )
        assert hmac.compare_digest(
            hmac.new(gateway.secret_key.encode(), msg.encode(), 'md5').hexdigest(),
            request.GET['hash'],
        )
        payment = Payment(
            gateway=gateway,
            payment_id=request.GET['PaymentOrderID'],
            order_id=request.GET['MerchantOrderNumber'],
            currency=request.GET['CurrencyID'],
            amount=int(request.GET['Amount']),
            base_units=int(request.GET['CurrencyBaseUnits']),
            status=int(request.GET['PaymentOrderStatusID']),
            status_description=request.GET['PaymentOrderStatusDescription'],
        )
    except (AssertionError, KeyError, ValueError):
        response.status_code = 400
    else:
        with transaction.atomic():
            payment.save()
    return response
