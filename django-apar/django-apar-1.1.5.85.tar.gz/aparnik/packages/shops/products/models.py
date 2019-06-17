# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Q, Count, Case, When, Value, BooleanField, Subquery, OuterRef
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from decimal import Decimal

from aparnik.utils.formattings import formatprice
from aparnik.utils.utils import round
from aparnik.contrib.settings.models import Setting
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.filefields.models import FileField

from aparnik.utils.fields import PriceField
from aparnik.contrib.sliders.models import SliderSegment

import decimal


# Create your models here.
# Product Manager
class ProductManager(BaseModelManager):

    def get_queryset(self):
        return super(ProductManager, self).get_queryset()

    def get_this_user(self, user):
        if not user.is_authenticated:
            return Product.objects.none()
        return self.get_queryset().all()

    def active(self, user=None):
        from aparnik.packages.shops.orders.models import Order
        from aparnik.packages.shops.productssharing.models import ProductSharing
        # TODO: Count is not correct
        return super(ProductManager, self).active(user=user).filter(is_draft=False).annotate(
            # user_invited_count_with_query=Count('productsharing_product', filter=ProductSharing.query_share_with(user, prefix='productsharing_product')),
            # is_user_invited_with_query=Case(When(user_invited_count_with_query__gte=1, then=Value(True)), default=Value(False),
            #                        output_field=BooleanField()),
            # my_product_count=Subquery(
            #     Order.objects..filter(
            #         is_paid=True,
            #         event=OuterRef('pk')
            #     ).values('event')
            #         .annotate(cnt=Count('pk'))
            #         .values('cnt'),
            #     output_field=models.IntegerField()
            # ),
            # my_product_count=Count('orderitem_set__order_obj', filter=Order.query_success('orderitem_set__order_obj', user=user)),
            # is_buy_with_query=Case(When(my_product_count__gte=1, then=Value(True)), default=Value(False), output_field=BooleanField()),
            # has_permit_with_query=Case(When(Q(Q(is_buy_with_query=True) | Q(is_free_field=True) | Q(is_user_invited_with_query=True)), then=Value(True)), default=Value(False), output_field=BooleanField()),
        )

    def get_wallet(self):
        return self.get(id=Setting.objects.get(key='PRODUCT_WALLET_ID').get_value())


# Product Model
class Product(BaseModel):
    # DELIVERY_TYPE status:
    DELIVERY_TYPE_SHIPPABLE = 'sh'
    DELIVERY_TYPE_DOWNLOADABLE = 'dw'
    DELIVERY_TYPE_CHOICES = (
        (DELIVERY_TYPE_SHIPPABLE, _('Shippable')),
        (DELIVERY_TYPE_DOWNLOADABLE, _('Downloadable')),
    )
    CURRENCY_IRR = 'IRR'
    CURRENCY_DOLLAR = 'D'
    CURRENCY_CHOICES = (
        (CURRENCY_IRR, _('IRR')),
        (CURRENCY_DOLLAR, _('Dollar')),
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    currency = models.CharField(max_length=10, default=CURRENCY_IRR, choices=CURRENCY_CHOICES, verbose_name=_('Currency'))
    price_fabric = PriceField(verbose_name=_('Price Fabric'))
    slider_segment_obj = models.ForeignKey(SliderSegment, null=True, blank=True, related_name='products_sliders', on_delete=models.CASCADE, verbose_name=_('Slider Segment'))
    is_free_field = models.BooleanField(default=False, verbose_name=_('Is Free'))
    discount_percent_value = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name=_('Discount Price'))
    discount_percent_expire = models.DateTimeField(null=True, blank=True, help_text=_('If blank, without expire'), verbose_name=_('Discount Expire'))
    is_discount_percent_expire_show = models.BooleanField(default=False, help_text=_('If True countdown is available'), verbose_name=_('Is Discount Expire Show'))
    is_tax = models.BooleanField(default=False, verbose_name=_('Is tax?'))
    delivery_type = models.CharField(max_length=10, blank=True, choices=DELIVERY_TYPE_CHOICES,
                                     verbose_name=_('Delivery type'))
    further_details = models.TextField(null=True, blank=True, verbose_name=_('Extra Description'))
    properties = models.ManyToManyField('ProductProperty', through='ProductPropertyMembership', verbose_name=_('Product Properties'))
    # این فیلد به درصد می باشد و در محاسبات تبدیل به تعداد بن خواهد شد
    aparnik_bon_return_value = models.IntegerField(default=-1,
                                                   validators=[MinValueValidator(-1), MaxValueValidator(100)],
                                                           help_text=_(
                                                               'If the number is set to -1, then the value in the settings will apply'),
                                                           verbose_name=_('Bon Return'))
    aparnik_bon_return_expire_value = models.IntegerField(default=-1,
                                                           help_text=_(
                                                               'If the number is set to -1, then the value in the settings will apply'),
                                                           verbose_name=_('Bon Return Expire ( Hours )'))
    # این فیلد به درصد می باشد و در محاسبات تبدیل به تعداد بن خواهد شد
    maximum_use_aparnik_bon_value = models.IntegerField(default=-1,
                                                        validators=[MinValueValidator(-2), MaxValueValidator(100)],
                                                        help_text=_(
                                                                      'If the number is set to -1, then the value in the settings will apply, If the number is set to -2, then no limitation execution.'),
                                                                  verbose_name=_('Maximum use aparnik bon'))
    has_permit_use_wallet_value = models.IntegerField(default=-1,
                                                validators=[MaxValueValidator(1), MinValueValidator(-1)],
                                                help_text=_('If the number is set to -1, then the value in the settings will apply'),
                                                verbose_name=_('Has Permit use wallet'))
    is_draft = models.BooleanField(default=False, verbose_name=_('Is draft'))

    objects = ProductManager()

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.is_buy_variable = None

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __unicode__(self):
        return '%s %s' % (self.id, self.title)

    @property
    def price(self):
        irt = 1
        if self.currency == self.CURRENCY_DOLLAR:
            irt = Setting.objects.get(key='DOLLAR_TO_IRR').get_value() / 10
        price_fabric = self.price_fabric * irt
        price = round(price_fabric - (price_fabric * decimal.Decimal(self.discount_percent / 100.0)))
        return price

    @property
    def price_fabric_string(self):
        return '%s' % formatprice.format_price(self.price_fabric)

    @property
    def price_string(self):
        return '%s' % formatprice.format_price(self.price)

    @property
    def discount_percent(self):
        if self.discount_percent_expire:
            return self.discount_percent_value if self.discount_percent_expire > now() else 0

        else:
            return self.discount_percent_value

    @property
    def is_free(self):
        return self.is_free_field

    # آیا این محصول جزو محصولات سابسکریپشن هست یا خیر
    # اگر هست باید از لینک های سابسکرایب خریداری بشه.
    @property
    def is_subscription(self):
        return self.subscriptions.active().count() > 0

    def buy_success(self, order):
        # override if you want custom process when order success
        pass

    def get_api_products_sharing_uri(self):
        return reverse('aparnik-api:shops:productssharing:product-user-share-list', args=[self.id])

    def get_api_product_sharing_add_uri(self):
        return reverse('aparnik-api:shops:productssharing:product-share-set', args=[self.id])

    # آیا این کاربر کالا را خریداری کرده است؟
    def is_buy(self, user):
        if self.is_buy_variable is not None:
            return self.is_buy_variable

        if not user.is_authenticated:
            return False

        from aparnik.packages.shops.orders.models import Order
        order = Order.objects.get_order_product(user=user, product=self)
        if order:
            self.is_buy_variable = True
            return self.is_buy_variable
        self.is_buy_variable = False
        return self.is_buy_variable

    # آیا این کاربر به این کالا دعوت شده است؟
    def is_user_invited(self, user):
        if not user.is_authenticated:
            return False
        from aparnik.packages.shops.productssharing.models import ProductSharing
        return ProductSharing.objects.share_with_this_user(user=user, product_id=self.id).exists()

    # بررسی دسترسی
    def has_permit(self, user):
        if self.is_free or self.is_user_invited(user) or self.is_buy(user):
            return True
        return False

    def get_title(self):
        return self.title

    def price_string_description(self, user):

        if not self.has_permit(user):
            return self.price_string

        if self.is_free:
            try:
                return Setting.objects.get(key='PRICE_PRODUCT_FREE_DESCRIPTION').get_value()
            except Exception as e:
                return 'رایگان'
        elif self.is_buy(user):
            try:
                return Setting.objects.get(key='PRICE_PRODUCT_BUY_DESCRIPTION').get_value()
            except Exception as e:
                return 'پرداخت شده'
        elif self.is_user_invited(user):
            try:
                return Setting.objects.get(key='PRICE_PRODUCT_SHARING_DESCRIPTION').get_value()
            except Exception as e:
                return 'دعوت شده'

        return self.price_string

    @property
    def aparnik_bon_return(self):
        value = self.aparnik_bon_return_value
        if value == -1:
            value = Setting.objects.get(key='APARNIK_BON_RETURN_DEFAULT_VALUE').get_value()
        value = ((self.price * value) / Decimal('100')) / Setting.objects.get(key='APARNIK_BON_VALUE').get_value()
        return value

    @property
    def aparnik_bon_return_value_string(self):
        price = round(self.aparnik_bon_return * Setting.objects.get(key='APARNIK_BON_VALUE').get_value())
        return '%s' % formatprice.format_price(price)

    @property
    def aparnik_bon_return_expire(self):
        value = self.aparnik_bon_return_expire_value
        if value == -1:
            value = Setting.objects.get(key='APARNIK_BON_RETURN_DEFAULT_EXPIRE_VALUE').get_value()
        return value

    @property
    def aparnik_bon_return_expire_date(self):
        value = self.aparnik_bon_return_expire
        if value == 0:
            return now() + relativedelta(years=200)
        return now() + relativedelta(hours=value)

    @property
    def maximum_use_aparnik_bon(self):
        value = self.maximum_use_aparnik_bon_value
        if value == -1:
            value = Setting.objects.get(key='MAXIMUM_USE_APARNIK_BON').get_value()
        if value == -2:
            import sys
            value = sys.maxsize

        value = ((self.price * value) / Decimal('100')) / Setting.objects.get(key='APARNIK_BON_VALUE').get_value()
        return value

    @property
    def has_permit_use_wallet(self):
        value = self.has_permit_use_wallet_value
        if value == -1:
            value = Setting.objects.get(key='HAS_PERMIT_DEFAULT_USE_WALLET').get_value()
        return value == 1


class ProductPropertyManager(models.Manager):

    def get_queryset(self):
        return super(ProductPropertyManager, self).get_queryset()

    def active(self):
        return self.get_queryset()


# Product Model
class ProductProperty(models.Model):

    icon = models.ForeignKey(FileField, on_delete=models.CASCADE, verbose_name=_('Icon'))
    title = models.CharField(max_length=100, verbose_name=_('Title'))

    objects = ProductPropertyManager()

    def __unicode__(self):
        return '%s %s' % (self.id, self.title)

    class Meta:
        verbose_name = _('Product Property')
        verbose_name_plural = _('Product Properties')


class ProductPropertyMembership(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    property = models.ForeignKey(ProductProperty, on_delete=models.CASCADE, verbose_name=_('Property'))
    value = models.CharField(max_length=255, verbose_name=_('Content'))

    class Meta:
        verbose_name = _('Product Property Membership')
        verbose_name_plural = _('Product Property Membership')

    def __unicode__(self):
        return self.value
