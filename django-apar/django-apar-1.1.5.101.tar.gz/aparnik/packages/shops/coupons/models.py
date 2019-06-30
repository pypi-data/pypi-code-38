# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError, MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
import uuid
from decimal import Decimal

from aparnik.utils.utils import field_with_prefix
from aparnik.utils.fields import *
from aparnik.settings import aparnik_settings

User = get_user_model()


# Create your models here.
# TODO: add validation for limited user custom user or all user when add
class CouponManager(models.Manager):

    def get_queryset(self):
        return super(CouponManager, self).get_queryset()

    def status(self, code, user, order):

        try:

            coupon = self.get_queryset().get(code=code)
        except:

            raise ValidationError({'coupon': [Coupon.get_status_description(Coupon.COUPON_STATUS_NOT_FOUND)]})

        # check min and max order
        if order.status != order.STATUS_WAITING:

            raise ValidationError({'coupon': [_('This order finished before.')]})
        if coupon.min_price_order > 0 and coupon.min_price_order > order.get_total_cost_order():

            raise ValidationError({'coupon': [
                Coupon.get_status_description(status_title=Coupon.COUPON_STATUS_ORDER_MINIMUM_IS_REQUIRED)]})

        if coupon.max_price_order > 0 and coupon.max_price_order < order.get_total_cost_order():

            raise ValidationError(
                {'coupon': [Coupon.get_status_description(Coupon.COUPON_STATUS_ORDER_MAXIMUM_IS_REQUIRED)]})

        # check expire date
        if coupon.expire_at is not None and coupon.expire_at < now():

            raise ValidationError({'coupon': [Coupon.get_status_description(Coupon.COUPON_STATUS_EXPIRED)]})

        # add coupon
        if coupon.for_users == Coupon.COUPON_FOR_ALL_USER and coupon.membership_set.filter(user=user,
                                                                                           is_redeem=True).count() == 0:

            return Coupon.COUPON_STATUS_OK
        elif coupon.for_users == Coupon.COUPON_FOR_CUSTOM_USER and coupon.membership_set.filter(user=user,
                                                                                                is_redeem=False).count() > 0:

            return Coupon.COUPON_STATUS_OK
        elif coupon.for_users == Coupon.COUPON_FOR_LIMITED_USER and coupon.membership_set.filter(
                is_redeem=True).count() <= coupon.for_limited_users_value:

            return Coupon.COUPON_STATUS_OK

        raise ValidationError({'coupon': [Coupon.get_status_description(Coupon.COUPON_STATUS_EXPIRED)]})

    def add_coupon(self, code, user, order):

        if Coupon.COUPON_STATUS_OK == self.status(code=code, user=user, order=order):
            try:

                coupon = self.get_queryset().get(code=code)
            except:

                raise ValidationError({'coupon': [Coupon.get_status_description(Coupon.COUPON_STATUS_NOT_FOUND)]})

            if Membership.objects.filter(user=user, coupon=coupon).count() == 0:
                membership = Membership.objects.create(user=user, coupon=coupon)
                membership.save()

            return coupon

        raise ValidationError({'coupon': [Coupon.get_status_description(Coupon.COUPON_STATUS_EXPIRED)]})


class Coupon(models.Model):
    # coupon status
    COUPON_STATUS_OK = 'o'
    COUPON_STATUS_REDEEM = 'r'
    COUPON_STATUS_EXPIRED = 'e'
    COUPON_STATUS_NOT_FOUND = 'nf'
    COUPON_STATUS_ORDER_MINIMUM_IS_REQUIRED = 'ominr'
    COUPON_STATUS_ORDER_MAXIMUM_IS_REQUIRED = 'omaxr'
    COUPON_STATUS_CHOICES = (
        (COUPON_STATUS_OK, _('Ok')),
        (COUPON_STATUS_REDEEM, _('The code was redeem.')),
        (COUPON_STATUS_EXPIRED, _('The code expired.')),
        (COUPON_STATUS_NOT_FOUND, _('The code does not exist.')),
        (COUPON_STATUS_ORDER_MINIMUM_IS_REQUIRED, _('Minimum price for order must greater than your order price.')),
        (COUPON_STATUS_ORDER_MAXIMUM_IS_REQUIRED, _('Maximum price for order must less than your order price.')),
    )

    COUPON_TYPE_PERCENT = 'p'
    COUPON_TYPE_VALUE = 'v'
    COUPON_TYPE_CHOICES = (
        (COUPON_TYPE_PERCENT, _('Percent')),
        (COUPON_TYPE_VALUE, _('Value')),

    )
    COUPON_FOR_ALL_USER = 'a'
    COUPON_FOR_LIMITED_USER = 'l'
    COUPON_FOR_CUSTOM_USER = 'c'
    COUPON_FOR_CHOICES = (
        (COUPON_FOR_ALL_USER, _('All user')),
        (COUPON_FOR_LIMITED_USER, _('Limited user')),
        (COUPON_FOR_CUSTOM_USER, _('Custom user')),
    )

    users = models.ManyToManyField(User, through='Membership', verbose_name=_('Membership'))
    code = models.CharField(max_length=10, blank=True, null=True, unique=True, verbose_name=_('Code'), help_text=_('If blank default no limitation.'))
    expire_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Expire at'), help_text=_('If blank default no limitation.'))
    value = PriceField(validators=[MinValueValidator(1)], verbose_name=_('Value'))
    type = models.CharField(max_length=2, choices=COUPON_TYPE_CHOICES, default=COUPON_TYPE_PERCENT, verbose_name=_('type'))
    max_price_order = PriceField(big=True, default=0, verbose_name=_('Max price of order'), help_text=_('If blank default no limitation.')) # hadaksar mablaghe factor
    min_price_order = PriceField(big=True, default=0, verbose_name=_('Min price of order'), help_text=_('If blank default no limitation.')) # hadaghal mablaghe factor
    for_users = models.CharField(max_length=2, choices=COUPON_FOR_CHOICES, default=COUPON_FOR_ALL_USER, verbose_name=_('For users'))
    for_limited_users_value = models.IntegerField(blank=True, null=True, verbose_name=_('Limited users value'))

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name=_('Created at'))
    update_at = models.DateTimeField(auto_now_add=False, auto_now=True, verbose_name=_('Update at'))

    objects = CouponManager()

    def clean(self, *args, **kwargs):
        super(Coupon, self).clean(*args, **kwargs)
        # Don't allow complete action entries.
        self.clean_fields()
        if self.type == Coupon.COUPON_TYPE_PERCENT and self.value > Decimal(100):
            raise ValidationError({'value': [_('Value cannot greater than 100.')]})

        if self.code is None:
            def generate():
                base = 4
                coupon_code = uuid.uuid4().__str__().replace('-', '')

                coupon_code = coupon_code[base:base + aparnik_settings.COUPON_CODE_LENGTH]
                if Coupon.objects.filter(code=coupon_code).count() > 0:
                    return generate()
                return coupon_code

            self.code = generate()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Coupon, self).save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')

    @staticmethod
    def get_status_description(status_title):

        for status in Coupon.COUPON_STATUS_CHOICES:
            if status[0] == status_title:
                return status[1]

        return None

    def status(self, user, order):
        # TODO: handle for user
        return Coupon.COUPON_STATUS_OK

    def calculate_discount(self, total_cost):

        if self.type == self.COUPON_TYPE_PERCENT:
            return total_cost * (self.value / Decimal('100'))
        # elif self.type == self.COUPON_TYPE_VALUE:
        else:
            return self.value

    def redeem(self, user):
        membership = Membership.objects.filter(user=user, coupon=self, is_redeem=False).first()
        membership.is_redeem = True
        membership.save()

    @staticmethod
    def sort_redeem(return_key='redeem', prefix=''):
        sort = {
            return_key: {
                'label': 'مصرف',
                'queryset_filter': Q(),
                'annotate_command': {
                    'sort_count':
                        Count(
                            field_with_prefix('pk', prefix=prefix),
                            filter=Q(**{field_with_prefix('is_redeem', prefix=prefix): True})
                        )
                },
                'key_sort': 'sort_count',
            }
        }
        return sort


class CouponAllUsersManager(CouponManager):

    def get_queryset(self):
        return super(CouponAllUsersManager, self).get_queryset().filter(for_users=Coupon.COUPON_FOR_ALL_USER)


class CouponForAllUser(Coupon):

    objects = CouponAllUsersManager()

    class Meta:
        proxy = True
        verbose_name = _('Coupon for all users')
        verbose_name_plural = _('Coupons for all users')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.for_users = Coupon.COUPON_FOR_ALL_USER
        return super(CouponForAllUser, self).save(*args, **kwargs)


class CouponLimitedUsersManager(CouponManager):

    def get_queryset(self):
        return super(CouponLimitedUsersManager, self).get_queryset().filter(for_users=Coupon.COUPON_FOR_LIMITED_USER)


class CouponForLimitedUser(Coupon):

    objects = CouponLimitedUsersManager()

    class Meta:
        proxy = True
        verbose_name = _('Coupon for limited users')
        verbose_name_plural = _('Coupons for limited users')

    def clean(self, *args, **kwargs):
        super(CouponForLimitedUser, self).clean(*args, **kwargs)
        if self.for_limited_users_value is None:
            raise ValidationError({'for_limited_users_value': [_('This field is requeired.')]})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.for_users = Coupon.COUPON_FOR_LIMITED_USER
        return super(CouponForLimitedUser, self).save(*args, **kwargs)


class CouponCustomUsersManager(CouponManager):

    def get_queryset(self):
        return super(CouponCustomUsersManager, self).get_queryset().filter(for_users=Coupon.COUPON_FOR_CUSTOM_USER)


class CouponForCoustomUser(Coupon):

    objects = CouponCustomUsersManager()

    class Meta:
        proxy = True
        verbose_name = _('Coupon for custom users')
        verbose_name_plural = _('Coupons for custom users')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.for_users = Coupon.COUPON_FOR_CUSTOM_USER
        return super(CouponForCoustomUser, self).save(*args, **kwargs)


# Membership
class Membership(models.Model):
    user = models.ForeignKey(User, related_name='coupons', on_delete=models.CASCADE, verbose_name=_('User'))
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name=_('Coupon'))
    is_redeem = models.BooleanField(default=False, verbose_name=_('Is redeem'))

    class Meta:
        verbose_name = _('Membership')
        verbose_name_plural = _('Memberships')
