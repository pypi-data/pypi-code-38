# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.core.validators import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from dateutil.relativedelta import relativedelta
from decimal import Decimal

from aparnik.settings import aparnik_settings
from django.db.models import Sum
from aparnik.utils.utils import round
from aparnik.utils.formattings import formatprice
from aparnik.utils.fields import *
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.bankaccounts.models import BankAccount

User = get_user_model()


# Create your models here.
class CoSaleManager(BaseModelManager):

    def get_queryset(self):
        return super(CoSaleManager, self).get_queryset()

    def active(self):
        return super(CoSaleManager, self).active().filter(is_active=True)

    def add_record(self, user_co_sale, user_bought, order):
        # TODO: how pay to user?
        # TODO: send notification
        cosale_obj = CoSale.objects.create(user_bought_obj=user_bought, user_co_sale_obj=user_co_sale, order_obj=order)
        return cosale_obj

    def change_order(self, order):
        try:
            co_sale = CoSale.objects.get(order_obj=order)
        except Exception as e:
            # نباید رکورد رو ادد کنیم بخاطر اینکه رکورد ها دارن از قسمت پیمنت های ثبت شده ادد میشن و
            # اگر اونجا ثبت نشدن یعنی پرداختی صورت نگرته !
            return CoSale.objects.none()
        # if not order.is_success and co_sale.status != CoSale.STATUS_ORDER_CANCEL:
        #     CoSaleHistory.objects.create(cosale_obj=co_sale, status=CoSale.STATUS_ORDER_CANCEL)
        # elif order.is_success and co_sale.status == CoSale.STATUS_ORDER_CANCEL:
        #     CoSaleHistory.objects.create(cosale_obj=co_sale, status=CoSale.STATUS_NOT_CLEARED)

    def summary(self, user):
        return CoSalePayment.objects.summary(user)

    def this_user(self, user, is_user_bought=False):
        if is_user_bought:
            return self.active().filter(user_bought_obj=user)
        return self.active().filter(user_co_sale_obj=user)

    def history(self, user, is_user_bought, start_date=None, end_date=None):
        from aparnik.packages.shops.orders.models import Order
        if not start_date:
            start_date = now().date()
        if not end_date:
            end_date = now()

        return self.this_user(user, is_user_bought).filter(Order.query_success('order_obj'),
                                                           Order.query_date('order_obj', start_date, end_date)).filter()

    def transaction_price(self, user, is_user_bought, start_date=None, end_date=None):
        if not start_date:
            start_date = now().date()
        if not end_date:
            end_date = now()
        return self.history(user, is_user_bought, start_date, end_date).aggregate(price=Sum('price'))['price'] or 0

    def transaction_price_string(self, user, is_user_bought, start_date=None, end_date=None):
        if not start_date:
            start_date = now().date()
            end_date = now()
        return '%s' % formatprice.format_price(
            self.history(user, is_user_bought, start_date, end_date).aggregate(price=Sum('price'))['price'] or 0)


class CoSale(BaseModel):
    STATUS_CLEARED = 'C'
    STATUS_NOT_CLEARED = 'NC'
    STATUS_THE_REQUEST_FOR_SETTLEMENT_HAS_BEEN_RECEIVED = 'RSHBR'
    STATUS_ORDER_CANCEL = 'OC'
    STATUS_TYPE = (
        # تسویه شده
        (STATUS_CLEARED, _('Cleared')),
        # تسویه نشده است
        (STATUS_NOT_CLEARED, _('Not Cleared')),
        # درخواست تسویه دریافت شده است
        (STATUS_THE_REQUEST_FOR_SETTLEMENT_HAS_BEEN_RECEIVED, _('The request for settlement has been received')),
        # سفارش کنسل شده است
        (STATUS_ORDER_CANCEL, _('Order Cancel')),
    )
    # کسی که خرید را انجام داده است.
    user_bought_obj = models.ForeignKey(User, related_name='cosale_user_bought', verbose_name=_('User Bought'))
    # کسی که دعوت کرده است.
    user_co_sale_obj = models.ForeignKey(User, related_name='cosale_user_co_sale', verbose_name=_('User Co Sale'))
    order_obj = models.ForeignKey('orders.Order', related_name='cosale_order', verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    price = PriceField(big=True, default=0, verbose_name=_('Price'))

    objects = CoSaleManager()

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(CoSale, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.order_obj)

    class Meta:
        verbose_name = _('Co Sale')
        verbose_name_plural = _('Co Sales')

    def calculate_share_price(self, user_co_sale):
        return (user_co_sale.co_sale_percentage / Decimal('100')) * self.order_obj.get_total_cost()

    @property
    def price_string(self):
        return '%s' % formatprice.format_price(self.price)

    # @staticmethod
    # def status_dictionary(status):
    #     for key, value in CoSale.STATUS_TYPE:
    #         if key == status:
    #             return {
    #                 'key': key,
    #                 'value': value
    #             }
    #     return None


def post_save_co_sale_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.price = round(instance.calculate_share_price(instance.user_co_sale_obj))
        instance.save()


post_save.connect(post_save_co_sale_receiver, sender=CoSale)


class CoSalePaymentManager(BaseModelManager):

    def get_queryset(self):
        return super(CoSalePaymentManager, self).get_queryset()

    def active(self):
        return super(CoSalePaymentManager, self).active()

    def this_user(self, user):
        return self.active().filter(user_bank_account_obj__user_obj=user)

    def history(self, user, start_date=None, end_date=None):
        if not start_date:
            start_date = now().date()
        if not end_date:
            end_date = now()

        return self.this_user(user).filter()

    def transaction_price(self, user, start_date=None, end_date=None):
        if not start_date:
            start_date = now().date()
        if not end_date:
            end_date = now()
        return self.history(user, start_date, end_date).aggregate(price=Sum('price'))['price'] or 0

    def transaction_price_string(self, user, start_date=None, end_date=None):
        if not start_date:
            start_date = now().date()
            end_date = now()
        return '%s' % formatprice.format_price(
            self.history(user, start_date, end_date).aggregate(price=Sum('price'))['price'] or 0)

    # بستانکار
    def creditor_price(self, user):
        start_date = now() + relativedelta(years=-10)
        cosale_price = CoSale.objects.transaction_price(user, False, start_date)
        payment_price = CoSalePayment.objects.transaction_price(user, start_date)
        return cosale_price - payment_price

    def summary(self, user):
        dict = []

        price = CoSalePayment.objects.creditor_price(user)
        key = 'NC'

        dict.append({
            'price': price,
            'price_string': formatprice.format_price(price),
            'status':
                {
                    "value": "تسویه نشده",
                    "key": key
                },
        })

        for (key, value) in CoSalePayment.STATUS_TYPE:
            price = CoSalePayment.objects.active().filter(user_bank_account_obj__user_obj=user, status=key).aggregate(price=Sum('price'))[
                        'price'] or 0.0
            dict.append({
                'price': price,
                'price_string': formatprice.format_price(price),
                'status':
                    {
                        "value": value,
                        "key": key
                    },
            })

        return dict


class CoSalePayment(BaseModel):
    STATUS_CLEARED = 'CL'
    STATUS_THE_REQUEST_FOR_SETTLEMENT_HAS_BEEN_RECEIVED = 'RSHBR'
    STATUS_CANCEL = 'C'
    STATUS_TYPE = (
        # تسویه شده
        (STATUS_CLEARED, _('Cleared')),
        # درخواست تسویه دریافت شده است
        (STATUS_THE_REQUEST_FOR_SETTLEMENT_HAS_BEEN_RECEIVED, _('The request for settlement has been received')),
        # کنسل شده
        (STATUS_CANCEL, _('Cancel')),
    )

    price = PriceField(big=True, verbose_name=_('Price'))
    user_bank_account_obj = models.ForeignKey(BankAccount, verbose_name=_('User Bank Account'))
    tracking_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Tracking Number'))
    status = models.CharField(max_length=10, choices=STATUS_TYPE,
                              default=STATUS_THE_REQUEST_FOR_SETTLEMENT_HAS_BEEN_RECEIVED,
                              verbose_name=_('Status'))

    objects = CoSalePaymentManager()

    def clean(self):
        if self.id:
            payment = CoSalePayment.objects.get(pk=self.id)
            if payment.price != self.price:
                raise ValidationError({'price': [_('You can\'t change price.')]})
        creditor = CoSalePayment.objects.creditor_price(self.user_bank_account_obj.user_obj)
        if self.price > creditor:
            raise ValidationError({'price': [_('Your price request is more than creditor.')]})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(CoSalePayment, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % self.id

    class Meta:
        verbose_name = _('Co Sale Payment')
        verbose_name_plural = _('Co Sale Payments')

    @property
    def price_string(self):
        return formatprice.format_price(self.price)
