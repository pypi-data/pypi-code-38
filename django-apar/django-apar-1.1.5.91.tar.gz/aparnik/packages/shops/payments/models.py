# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import uuid

from aparnik.settings import Setting
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.packages.shops.orders.models import Order

User = get_user_model()
# Create your models here.


class PaymentManager(BaseModelManager):

    def get_queryset(self):
        return super(PaymentManager, self).get_queryset().order_by('-update_at')

    def get_this_user(self, user):
        if not user.is_authenticated:
            return Payment.objects.none()

        return self.get_queryset().filter(user=user)

    def get_paid(self, user, transaction):
        return self.get_this_user(user=user).filter(transaction=transaction).filter(status=Payment.STATUS_COMPLETE)

    def request_pay(self, order, method, user, call_back_url=""):
        # type: (object, object, object, object) -> object
        # TODO: before pay check order allow or canceled
        return Payment.objects.create(user=user, method=method, status=Payment.STATUS_WAITING, order_obj=order, call_back_url=call_back_url)


class Payment(BaseModel):
    # Method:
    METHOD_BANK = 'b'
    METHOD_WALLET = 'w'
    METHOD_CHOICES = (
        (METHOD_BANK, _('Bank')),
        (METHOD_WALLET, _('Wallet')),
    )
    # Status
    STATUS_CANCEL = 'c'
    STATUS_CANCEL_USER_PAY = 'cup'
    STATUS_CANCEL_SYSTEM = 'cs'
    STATUS_CANCEL_WALLET_DOES_NOT_CHARGE = 'cwn'
    STATUS_COMPLETE = 'co'
    STATUS_WAITING = 'w'
    STATUS_CHOICES = (
        (STATUS_CANCEL, _('Cancel')),
        (STATUS_CANCEL_SYSTEM, _('Cancel by system')),
        (STATUS_CANCEL_SYSTEM, _('Cancel by user after pay begin')),
        (STATUS_COMPLETE, _('Complete')),
        (STATUS_WAITING, _('Waiting')),
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_('Reference ID'))
    bank_reference = models.CharField(max_length=50, editable=False, blank=True, null=True, verbose_name=_('Bank Reference ID'))
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, verbose_name=_('User'))
    method = models.CharField(max_length=3, editable=False, choices=METHOD_CHOICES, verbose_name=_('Method payment'))
    status = models.CharField(max_length=10, editable=False, choices=STATUS_CHOICES, verbose_name=_('Status'))
    order_obj = models.ForeignKey(Order, editable=False, related_name='payments', on_delete=models.CASCADE, verbose_name=_('Order'))
    call_back_url = models.CharField(max_length=255, editable=False, blank=True, null=True, verbose_name=_('Call Back URL'))

    objects = PaymentManager()

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        return " %s - %s" %(self.user, self.method)

    def clean(self):
        # Don't allow complete action entries.
        if self.id:
            obj = Payment.objects.get(id=self.id)
        else:
            obj = self
        if obj.status != Payment.STATUS_WAITING or obj.order_obj.status != Payment.STATUS_WAITING:
            raise ValidationError(_('payment finish before.'))

        if obj.status == Payment.STATUS_WAITING and obj.method == Payment.METHOD_BANK and not obj.call_back_url:
            raise ValidationError(_('payment for bank must fill call back url.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Payment, self).save(*args, **kwargs)

    def get_url(self):
        if self.method == Payment.METHOD_WALLET:
            return reverse('aparnik-api:shops:payments:payment', args=[self.uuid])
        return reverse('aparnik:shops:payments:payment', args=[self.uuid]) #kwargs={'app_label': 'auth'}

    def get_method_json_display(self):
        icon = ""
        if self.method == Payment.METHOD_BANK:
            icon = "http://www.freeiconspng.com/uploads/bank-account-integration-with-existing-bank-accounts-for-inclusion--22.png"
        else:
            icon = 'http://www.freeiconspng.com/uploads/wallet-icon-7.png'
        json = {
            # TODO: change icon
            'icon': icon,
            'name': self.get_method_display()
        }
        return json

    def get_api_pay_cancel_uri(self):
        return reverse('aparnik-api:shops:payments:cancel', args=[self.uuid])

    def get_call_back_url(self):
        status = 0
        if self.status == Payment.STATUS_COMPLETE:
            status = 1

        import urllib.request, urllib.parse, urllib.error
        paramters = {
            'status': status,
            'date': self.created_at,
            'price': self.order_obj.total_cost_string.encode('utf8'),
            'refrence-id': self.uuid,
            'title': self.order_obj.items.first().product_obj.title.encode('utf8')
        }

        return self.call_back_url + '?' + urllib.parse.urlencode(paramters)

    def success(self):
        from aparnik.packages.shops.vouchers.models import Voucher
        if self.order_obj.is_allow_to_pay():
            self.status = Payment.STATUS_COMPLETE
            if self.method == self.METHOD_WALLET:
                self.user.wallet = self.user.wallet - self.order_obj.get_total_cost()
                if self.user.wallet < 0:
                    self.status = Payment.STATUS_CANCEL_WALLET_DOES_NOT_CHARGE
                    self.save()
                    charge_wallet_message = Setting.objects.get(key='WALLET_CHARGING_MESSAGE').get_value()
                    raise ValidationError(
                        # {'order': [_('Your wallet does not charge. Please charge it first.')]})
                        {'order': [charge_wallet_message]})

                Voucher.objects.redeem_for_order(self.order_obj)
                self.user.save()
            else:
                Voucher.objects.redeem_for_order(self.order_obj)

        else:
            self.status = Payment.STATUS_CANCEL_SYSTEM
        self.save()

        if self.status == Payment.STATUS_CANCEL_SYSTEM:
            raise ValidationError({'order': [_('You\'re order has been canceled by system. Please contact with shopkeeper.')]})

    def cancel(self):
        self.status = Payment.STATUS_CANCEL
        self.save()

    def is_success(self):
        return self.status == Payment.STATUS_COMPLETE


def post_save_payment_receiver(sender, instance, created, *args, **kwargs):

    if instance.status == Payment.STATUS_COMPLETE:
        from aparnik.packages.shops.products.models import Product
        wallet_id = Product.objects.get_wallet().id
        instance.order_obj.pay_success()

        try:
            sync_api_address_url = Setting.objects.active().get(key='ORDER_SYNC_WITH_WEBSITES').get_value()
            secret_key = Setting.objects.active().get(key='SECRET_KEY').get_value()
            import requests
            params = {'secret_key': secret_key, 'username': instance.order_obj.user.username,
                                    'products_id': ",".join(
                                        str(item.product_obj.pk) for item in instance.order_obj.items.all())}
            r = requests.post(sync_api_address_url,
                              data=params)

            if r.status_code == 200:
                instance.order_obj.is_sync_with_websites = True
                instance.order_obj.save()
        except:
            pass

        # check invite and etc.
        for item in instance.order_obj.items.all():

            if item.product_obj.id == wallet_id:
                return

        # فرد دعوت شده است یا خیر
        if instance.order_obj.user.invite.first():
            from aparnik.packages.shops.cosales.models import CoSale
            # کسی که دعوت کرده
            invited_by = instance.order_obj.user.invite.first().invited_by
            CoSale.objects.add_record(user_bought=instance.order_obj.user, user_co_sale=invited_by, order=instance.order_obj)

    elif instance.status == Payment.STATUS_CANCEL_SYSTEM:
        instance.order_obj.cancel()


post_save.connect(post_save_payment_receiver, sender=Payment)
