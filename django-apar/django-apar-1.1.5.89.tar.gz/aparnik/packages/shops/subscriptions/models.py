# -*- coding: utf-8 -*-


from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.validators import ValidationError

from dateutil.relativedelta import relativedelta

from aparnik.packages.shops.products.models import Product, ProductManager


User = get_user_model()


# Create your models here.
class SubscriptionManager(ProductManager):

    def get_queryset(self):
        return super(SubscriptionManager, self).get_queryset()

    def active(self, user=None):
        return super(SubscriptionManager, self).active(user=user)


class Subscription(Product):
    TYPE_ALL = 'a'
    TYPE_CUSTOM = 'c'
    TYPE_CHOICES = (
        (TYPE_ALL, _('All')),
        (TYPE_CUSTOM, _('Custom')),
    )

    type = models.CharField(max_length=5, default=TYPE_ALL, choices=TYPE_CHOICES, verbose_name=_('Type'))
    duration = models.DurationField(default='30 00:00:00', verbose_name=_('Duration'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    orders = models.ManyToManyField('orders.Order', through='SubscriptionOrder', verbose_name=_('Orders'))
    products = models.ManyToManyField('products.Product', blank=True, related_name='subscriptions', verbose_name=_('Products'))

    objects = SubscriptionManager()

    def buy_success(self, order):
        expire_at = now() + self.duration
        try:
            subscription_order = SubscriptionOrder.objects.get(subscription_obj=self, order_obj=order)
            subscription_order.expire_at = expire_at
            subscription_order.save()
        except:
            SubscriptionOrder.objects.create(
                subscription_obj=self,
                order_obj=order,
                expire_at=expire_at,
            )
        return super(Subscription, self).buy_success(order)

    def is_buy(self, user):

        is_buy = super(Subscription, self).is_buy(user=user)

        if is_buy:
            return self.subscriptionorder_set.active().exists()

        return False

    def price_string_description(self, user):

        if self.is_buy(user):
            days_remain = abs((now() - self.subscriptionorder_set.active().first().expire_at).days)
            return '%s روز دیگر باقی مانده' %days_remain
        return super(Subscription, self).price_string_description(user=user)

    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def clean(self):
        # if self.type == self.TYPE_ALL and self.products.count() > 0:
        #     raise ValidationError({
        #         'type': [_(
        #             'You can not choice product when select the subscription for all products.'
        #         )]})
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Subscription, self).save(*args, **kwargs)


class SubscriptionOrderManager(models.Manager):

    def get_queryset(self):
        return super(SubscriptionOrderManager, self).get_queryset()

    def active(self):
        return self.get_queryset().filter(expire_at__gte=now())


class SubscriptionOrder(models.Model):

    subscription_obj = models.ForeignKey(Subscription, on_delete=models.CASCADE, verbose_name=_('Subscription'))
    order_obj = models.ForeignKey('orders.Order', on_delete=models.CASCADE, verbose_name=_('Order'))
    expire_at = models.DateTimeField(auto_now_add=False, auto_now=False, verbose_name=_('Expire at'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = SubscriptionOrderManager()

    def __str__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = _('Subscription Order')
        verbose_name_plural = _('Subscriptions Orders')
