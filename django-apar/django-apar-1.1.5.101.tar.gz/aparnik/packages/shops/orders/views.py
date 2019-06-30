# -*- coding: utf-8 -*-


from django.shortcuts import render, get_object_or_404

from aparnik.settings import Setting
from aparnik.utils.formattings import formatprice
from aparnik.packages.shops.orders.models import Order
from aparnik.packages.shops.payments.models import Payment
from aparnik.contrib.province.models import City


# Create your views here.
def invoice(request, uuid):

    order = get_object_or_404(Order, uuid=uuid)
    if order.is_success:
        url = None
    else:
        payment = Payment.objects.request_pay(order=order, method=Payment.METHOD_BANK, call_back_url=request.build_absolute_uri(order.get_pay_uri()), user=order.user)
        url = request.build_absolute_uri(payment.get_url())

    logo = Setting.objects.get(key='LOGO_PROJECT_ICON').get_value()
    mohr = Setting.objects.get(key='MOHR_ICON').get_value()
    project_name = Setting.objects.get(key='PROJECT_NAME').get_value()
    economical_number = Setting.objects.get(key='ECONOMICAL_NUMBER').get_value()
    registration_number = Setting.objects.get(key='REGISTRATION_NUMBER').get_value()
    postal_code = Setting.objects.get(key='POSTAL_CODE').get_value()
    city = City.objects.get(id=Setting.objects.get(key='PROJECT_CITY_ID').get_value())
    address = Setting.objects.get(key='ADDRESS').get_value()
    phone = Setting.objects.get(key='PHONE').get_value()
    # چون هر روز ممکنه تغییر کنه این کار منطقی نیست
    dollar_price = '%s' % formatprice.format_price(Setting.objects.get(key='DOLLAR_TO_IRR').get_value() / 10)

    context = {
        'order': order,
        'url_pay': url,
        'customer_address': order.address_obj,
        'logo_small': logo,
        'mohr': mohr,
        'company_name': project_name,
        'economical_number': economical_number,
        'registration_number': registration_number,
        'postal_code': postal_code,
        'city': city,
        'address': address,
        'phone': phone,
        'dollar_price': dollar_price,
    }
    template_name = 'orders/invoice.html'
    return render(request, template_name=template_name, context=context)
