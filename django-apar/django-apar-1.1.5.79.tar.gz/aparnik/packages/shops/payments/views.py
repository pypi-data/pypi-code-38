# -*- coding: utf-8 -*-


from django.shortcuts import render, get_list_or_404

from aparnik.settings import aparnik_settings
from .models import Payment
from aparnik.packages.shops.zarinpals.views import send_request


# Create your views here.
def payment(request, uuid):
    payments_obj = get_list_or_404(Payment.objects.all(), uuid=uuid)
    pay_obj = payments_obj[0]

    if pay_obj.order_obj.status == Payment.STATUS_WAITING and pay_obj.status == Payment.STATUS_WAITING:

        if aparnik_settings.BANK_ACTIVE:
            # (bank_obj, created) = BankAPI.objects.get_or_create(amount=pay_obj.transaction.amount, invoice_number=pay_obj.uuid.int)
            return send_request(request, pay_obj)
        else:
            pay_obj.success()

    if pay_obj.is_success():
        return render(request=request, template_name='suit/paysuc.html', status=200, context={'obj': pay_obj})

    return render(request=request, template_name='suit/payunsuc.html', status=400, context={'obj': pay_obj})
