# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from zeep import Client

from aparnik.packages.shops.payments.models import Payment
from aparnik.settings import aparnik_settings, Setting
from .models import Bank


def send_request(request, payment):
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    order = payment.order_obj
    description = 'خرید %s' %(order.items.first().product_obj.title)
    call_back_url = request.build_absolute_uri(reverse('aparnik:shops:zarinpals:verify', args=[payment.uuid]))
    merchent_code = Setting.objects.get(key='ZARINPAL_MERCHENT_CODE').get_value()
    result = client.service.PaymentRequest(
        merchent_code,
        order.get_total_cost(),
        description,
        '',
        '',
        call_back_url
    )
    if result.Status == 100:
        bank = Bank.objects.create(authority_id=result.Authority,
                                   status=result.Status,
                                   payment=payment)
        return redirect('https://www.zarinpal.com/pg/StartPay/%s/ZarinGate' %(str(result.Authority)))
    else:
        raise Http404 #HttpResponse('Error code: ' + str(result.Status))


def verify(request, uuid):
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    payment = get_object_or_404(Payment, uuid=uuid)

    if payment.status != Payment.STATUS_WAITING:
        raise Http404

    merchent_code = Setting.objects.get(key='ZARINPAL_MERCHENT_CODE').get_value()
    result = client.service.PaymentVerification(merchent_code, request.GET['Authority'], payment.order_obj.get_total_cost())
    bank = get_object_or_404(Bank, authority_id=request.GET['Authority'])

    if bank.payment != payment:
        raise Http404

    bank.ref_id = result.RefID
    bank.status = result.Status
    bank.save()
    if result.Status == 100 or result.Status == 101:
        payment.success()
    else:
        # return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
        payment.cancel()

    # response = HttpResponse("", status=302)
    # url = bank_obj.get_form_url()
    # response['Location'] = url
    # response['Location'] = payment.get_call_back_url()

    # return response
    from aparnik.packages.shops.payments.views import payment as payment_view
    return payment_view(request, uuid=payment.uuid)
    # return render(request=request, template_name='suit/payunsuc.html', context={'obj': payment}, status=400)
