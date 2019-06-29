# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

import datetime
from dateutil.relativedelta import relativedelta
from aparnik.settings import Setting
from aparnik.utils.utils import round, field_with_prefix
from aparnik.utils.formattings import formatprice
from aparnik.utils.fields import *
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager

User = get_user_model()


# Create your models here.
class VoucherManager(BaseModelManager):

    def get_queryset(self):
        return super(VoucherManager, self).get_queryset()

    def active(self, only_accessible=True):
        dict = {
            'is_active': True,
        }

        if only_accessible:
            dict['expire_at__date__gte'] = now()
            dict['is_spent'] = False

        return super(VoucherManager, self).active().filter(**dict)

    def this_user(self, user, only_accessible=True):
        return self.active(only_accessible).filter(user_obj=user)

    def add_voucher_by_admin_command(self, user, quantity, description):
        from aparnik.packages.shops.orders.models import Order, Product
        product = Product.objects.get(id=Setting.objects.get(key='MANAGER_PRODUCT_ID').get_value())
        order = Order.objects.create(user=user)
        order.add_item(product, quantity, description)
        #  متد سیو باید فراخوانی شود که وچر ادد آیتم آن شروع به کار کند و رکورد متناظر با آن ذخیره شود.
        order.save()
        order.pay_success()
        voucher = Voucher.objects.get(order_item_obj=order.items.first(), user_obj=user)
        voucher.quantity = quantity
        voucher.quantity_remain = quantity
        voucher.save()


    def quantities_accessible(self, user):
        # from aparnik.packages.shops.orders.models import Order
        # filter(Order.query_success('order_item_obj__order_obj')).
        return self.this_user(user).aggregate(quantities=Sum('quantity_remain'))['quantities'] or 0

    def price_accessible(self, user):
        quantities = self.quantities_accessible(user)
        price = round(quantities * Setting.objects.get(key='APARNIK_BON_VALUE').get_value())
        return price

    def price_accessible_string(self, user):
        return '%s' % formatprice.format_price(self.price_accessible(user))

    def quantities_accessible_on_order(self, order):
        max_order_bon = 0
        try:
            max_order_bon = int(order.get_total_cost_order() / Setting.objects.get(key='APARNIK_BON_VALUE').get_value())
        except:
            pass
        if order.is_success:
            return VoucherOrderItem.objects.active().filter(item_obj__order_obj=order).aggregate(
                quantities=Sum('quantity_usage'))['quantities'] or 0
        quantity_order = 0
        for item in order.items.all():
            quantity_order = quantity_order + item.maximum_use_aparnik_bon
            if quantity_order >= max_order_bon:
                quantity_order = max_order_bon
                break

        quantity_user = self.quantities_accessible(order.user)

        # اگر تعداد بن های قابل استفاده در فاکتور بیشتر از بن های یوزر بود که بن های یوزر برگشت داده میشود و گرنه...
        if quantity_order > quantity_user:
            return quantity_user

        return quantity_order

    def price_accessible_on_order(self, order):
        quantities = self.quantities_accessible_on_order(order)
        price = round(quantities * Setting.objects.get(key='APARNIK_BON_VALUE').get_value())
        return price

    def price_accessible_on_order_string(self, order):
        return '%s' % formatprice.format_price(self.price_accessible_on_order(order))

    def change_order(self, order):
        # TODO: if change send notifications
        for item in order.items.all():
            try:
                voucher = self.get_queryset().get(order_item_obj=item)
                voucher.quantity = item.aparnik_bon_return
                voucher.is_active = order.is_success
                voucher.save()

            except:
                if not order.is_success or (item.aparnik_bon_return == 0 and item.product_obj.pk != Setting.objects.get(key='MANAGER_PRODUCT_ID').get_value()):
                    break

                voucher = Voucher.objects.create(
                    order_item_obj=item,
                    quantity=item.aparnik_bon_return,
                    quantity_remain=item.aparnik_bon_return,
                    user_obj=order.user,
                    expire_at=item.product_obj.aparnik_bon_return_expire_date
                )

    def redeem_for_order(self, order):
        # این فیلد بررسی می کنه از سقف این یوزر بیشتر مصرف نشه.
        allow_vouchers_quantity = self.quantities_accessible(order.user)
        # این فیلد مقدار مصرف شده رو نگه میداره
        total_usage = 0
        queryset = Voucher.objects.this_user(order.user).order_by('-quantity_remain')
        items = sorted(order.items.all(), key=lambda x: x.maximum_use_aparnik_bon, reverse=True)

        for item in items:
            quantity = item.maximum_use_aparnik_bon
            for voucher in queryset.all():
                q = 0
                # اینجا بررسی می کنیم آیا مقدار مصرف شده به حد مجاز رسیده یا خیر
                if total_usage >= allow_vouchers_quantity:
                    break
                # بررسی صورت می گیرد که مقدار باقی مانده این Voucher بیشتر است یا مقدار مورد نیاز این آیتم برای مصرف بن
                if voucher.quantity_remain >= quantity:
                    q = quantity
                else:
                    q = voucher.quantity_remain
                # اینجا چک می کنیم اگر مجموع یک آیتم از حد مجاز بیشتر شده باشه تا سقف مجاز برداشت بن صورت بگیره.
                if total_usage + q >= allow_vouchers_quantity:
                    q = allow_vouchers_quantity - total_usage

                total_usage = total_usage + q

                VoucherOrderItem.objects.create(
                    voucher_obj=voucher,
                    item_obj=item,
                    quantity_usage=q,
                )
                if quantity - q == 0:
                    break
                quantity = quantity - q


class Voucher(BaseModel):
    user_obj = models.ForeignKey(User, related_name='voucher_user', on_delete=models.CASCADE, verbose_name=_('User'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    quantity_remain = models.PositiveIntegerField(default=0, verbose_name=_('Quantity Remain'))
    # آیتمی که به واسطه آن این کوپن بوجود آمده است و کاربر می تواند استفاده کند .
    order_item_obj = models.OneToOneField('orders.OrderItem', related_name='voucher_order_item', on_delete=models.CASCADE, verbose_name=_('Order Item'))
    expire_at = models.DateTimeField(default=datetime.datetime(2300, 10, 5, 18, 00), verbose_name=_('Expire at'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_spent = models.BooleanField(default=False, verbose_name=_('Is spent'))
    order_item_obj_spent = models.ManyToManyField('orders.OrderItem', through='VoucherOrderItem', related_name='voucher_order_item_spent', verbose_name=_('Item Spent this voucher'))

    objects = VoucherManager()

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Voucher, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order_item_obj)

    class Meta:
        verbose_name = _('Voucher')
        verbose_name_plural = _('Vouchers')

    @property
    def price(self):
        price = round(self.quantity * Setting.objects.get(key='APARNIK_BON_VALUE').get_value())
        return price

    @property
    def price_string(self):
        return '%s' % formatprice.format_price(self.price)

    @staticmethod
    def sort_voucher(return_key='voucher', prefix=''):
        sort = {
            return_key: {
                'label': 'بن های هدیه',
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Coalesce(Sum(
                            field_with_prefix('quantity_usage', prefix=prefix),
                        ), 0)
                },
                'key_sort': 'sort_count',
            }
        }
        return sort

class VoucherOrderItemManager(models.Manager):
    def get_queryset(self):
        return super(VoucherOrderItemManager, self).get_queryset()

    def active(self):
        return self.get_queryset()


class VoucherOrderItem(models.Model):
    voucher_obj = models.ForeignKey(Voucher, related_name='voucher_model', on_delete=models.CASCADE, verbose_name=_('Voucher'))
    item_obj = models.ForeignKey('orders.OrderItem', related_name='voucher_item_spent', on_delete=models.CASCADE, verbose_name=_('Item Spent'))
    quantity_usage = models.IntegerField(default=0, verbose_name=_('Quantity Usage'))
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = VoucherOrderItemManager()

    class Meta:
        verbose_name = _('Voucher Order Item')
        verbose_name_plural = _('Voucher Order Items')

    def clean(self):
        queryset = VoucherOrderItem.objects.active().filter(voucher_obj=self.voucher_obj)
        if self.id:
            queryset = queryset.exclude(pk=self.id)

        quantity_spent = (queryset.aggregate(quantities=Sum('quantity_usage'))['quantities'] or 0) + self.quantity_usage

        if quantity_spent > self.voucher_obj.quantity:
            raise ValidationError({'quantity_usage': [_('Total quantity usage doesnt match.'), ]})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(VoucherOrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.voucher_obj)


def post_save_voucher_order_item_receiver(sender, instance, created, *args, **kwargs):
    voucher_obj = instance.voucher_obj
    quantity = VoucherOrderItem.objects.active().filter(voucher_obj=voucher_obj).aggregate(quantities=Sum('quantity_usage'))['quantities'] or 0
    voucher_obj.is_spent = quantity == voucher_obj.quantity
    voucher_obj.quantity_remain = voucher_obj.quantity - quantity
    voucher_obj.save()


post_save.connect(post_save_voucher_order_item_receiver, sender=VoucherOrderItem)
