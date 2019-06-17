# -*- coding: utf-8 -*-


from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now

from decimal import Decimal
import uuid

from aparnik.utils.utils import round
from aparnik.utils.fields import PriceField
from aparnik.utils.formattings import formatprice
from aparnik.settings import Setting
from aparnik.contrib.basemodels.models import BaseModel, BaseModelManager
from aparnik.contrib.addresses.models import UserAddress
from aparnik.contrib.notifications.models import NotificationForSingleUser, Notification
from aparnik.packages.shops.products.models import Product
from aparnik.packages.shops.coupons.models import Coupon, CouponForCoustomUser

User = get_user_model()


# Create your models here.


class OrderManager(BaseModelManager):

    def get_queryset(self):
        return super(OrderManager, self).get_queryset()

    def get_this_user(self, user, custom_type=None):
        if not user.is_authenticated:
            return Order.objects.none()
        queryset = self.get_queryset().filter(user=user)
        if custom_type:
            queryset = queryset.filter(
                items__product_obj__polymorphic_ctype=ContentType.objects.get_for_model(custom_type))
        return queryset

    def get_this_user_bought(self, user, custom_type=None):
        return self.get_this_user(user, custom_type).filter(Order.query_success())

    def get_order_product(self, user, product):
        from aparnik.packages.shops.subscriptions.models import Subscription
        buy = self.get_this_user(user=user).filter(
            Order.query_success()
        ).filter(
            Q(items__product_obj=product) |
            (
                    Q(
                        subscriptionorder__expire_at__gte=now(),
                        subscriptionorder__subscription_obj__type=Subscription.TYPE_ALL
                    ) |
                    Q(
                        subscriptionorder__expire_at__gte=now(),
                        subscriptionorder__subscription_obj__type=Subscription.TYPE_CUSTOM,
                        subscriptionorder__subscription_obj__products=product
                    )
            )
        )
        if buy:
            return buy.first()
        return None

    def get_order_products(self, products):
        orders = self.get_queryset().filter(
            Order.query_success()).filter(items__product_obj__id__in=products)
        return orders


class Order(BaseModel):
    # Status:
    STATUS_CANCEL = 'c'
    STATUS_COMPLETE = 'co'
    STATUS_DISPUTED = 'd'
    STATUS_CHALLENGED = 'ch'
    STATUS_WAITING = 'w'
    STATUS_PAID = 'pa'
    STATUS_PAID_BY_WEBSITE = 'paw'
    STATUS_CHOICES = (
        (STATUS_WAITING, _('Waiting')),
        (STATUS_PAID, _('Paid')),
        (STATUS_PAID_BY_WEBSITE, _('Paid by website')),
        (STATUS_CANCEL, _('Cancel')),
        (STATUS_COMPLETE, _('Complete')),
        (STATUS_DISPUTED, _('Disputed')),
        (STATUS_CHALLENGED, _('Challenged')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    coupon = models.ForeignKey(Coupon, related_name='orders', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name=_('Coupon'))
    status = models.CharField(max_length=5, default=STATUS_WAITING, choices=STATUS_CHOICES, verbose_name=_('Status'))
    address_obj = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True, blank=True,
                                    verbose_name=_('Order Address'))
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name=_('Reference ID'))
    postal_cost_value = PriceField(big=True, default=0, verbose_name=_('Postal Cost'))
    is_sync_with_websites = models.BooleanField(default=False, verbose_name=_('Is sync with websites'))

    objects = OrderManager()

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return '{}'.format(self.id)

    @staticmethod
    def query_success(prefix='', user=None):
        from aparnik.packages.shops.subscriptions.models import Subscription
        field_subscription = 'subscriptionorder'
        field_status = 'status'
        field_user = 'user'
        if prefix:
            field_status = prefix + '__' + field_status
            field_user = prefix + '__' + field_user
            field_subscription = prefix + '__' + field_subscription

        query_filter_status = Q(Q(**{field_status: Order.STATUS_COMPLETE}) | \
                       Q(**{field_status: Order.STATUS_PAID}) | \
                       Q(**{field_status: Order.STATUS_PAID_BY_WEBSITE}))
        # TODO: چطوری میتونیم یک کوئری مثل منیجر در حالت کلی بنویسیم که بتونیم متوجه بشیم که این محصول خریداری شده یا نه
        # query_filter_subscription = Q(
        #     Q(
        #         **{field_subscription + '__expire_at__gte': now(),
        #            field_subscription + '__subscription_obj__type': Subscription.TYPE_ALL,
        #            }
        #     ) |
        #     Q(
        #         **{
        #             field_subscription + '__expire_at__gte': now(),
        #             field_subscription + '__subscription_obj__type': Subscription.TYPE_CUSTOM,
        #             # subscriptionorder__subscription_obj__products=product,
        #         }
        #     )
        # )

        query_filter_user = Q()
        if user:
            query_filter_user = Q(Q(**{field_user: user}))

        return Q(query_filter_status, query_filter_user)

    @staticmethod
    def query_waiting(prefix=''):
        field = 'status'
        if prefix:
            field = prefix + '__' + field
        return Q(**{field: Order.STATUS_WAITING})

    @staticmethod
    def query_cancel(prefix=''):
        field = 'status'
        if prefix:
            field = prefix + '__' + field
        return Q(**{field: Order.STATUS_CANCEL})

    @staticmethod
    def query_date(prefix='', start_date=None, end_date=None):

        if not start_date:
            start_date = now().date()
        if not end_date:
            end_date = now()
        field = 'payments__update_at__range'
        if prefix:
            field = prefix + '__' + field
        return Q(**{field: [start_date, end_date]})

    # def get_api_uri(self):
    #     return reverse('aparnik-api:shops:orders:detail', args=[self.id])

    def get_api_request_pay_uri(self):
        return reverse('aparnik-api:shops:orders:request-pay', args=[self.id])

    def get_api_coupon_uri(self):
        return reverse('aparnik-api:shops:orders:coupon', args=[self.id])

    def get_api_add_address_uri(self):
        return reverse('aparnik-api:shops:orders:add-address', args=[self.id])

    def get_api_add_item_uri(self):
        return reverse('aparnik-api:shops:orders:add-item', args=[self.id])

    def get_pay_uri(self):
        return reverse('aparnik:shops:orders:invoice', args=[self.uuid])

    # Mablaghe faktor
    def get_total_cost_order(self):
        return round(sum(item.get_cost() for item in self.items.all()))

    @property
    def total_cost_order_string(self):
        return '%s' % formatprice.format_price(self.get_total_cost_order())

    # mablaghe ghabele pardakht
    def get_total_cost(self):
        total_cost = self.get_total_cost_order()

        return round(total_cost + self.postal_cost - self.get_discount() - self.get_bon_price())

    @property
    def total_cost_string(self):
        return '%s' % formatprice.format_price(self.get_total_cost())

    # مبلغ به حروف
    @property
    def total_cost_to_word(self):
        return formatprice.format_price(self.get_total_cost(), str('%ic=t:%se=,:%cu=t:%StrTr=True'))

    @property
    def order_code(self):
        orderCode = ('%s' % (Setting.objects.get(key='ORDER_CODE_PREFIX')).get_value() + '%s' % str(self.id))
        return orderCode

    # takhfif
    def get_discount(self):
        total_cost = self.get_total_cost_order()
        discount = 0
        if self.coupon is not None:
            discount = self.coupon.calculate_discount(total_cost=total_cost)

        return round(discount)

    @property
    def postal_cost(self):
        if self.is_success:
            return self.postal_cost_value
        postal_cost = Setting.objects.get(key='POSTAL_COST').get_value()
        return postal_cost

    @property
    def postal_cost_string(self):
        postal_cost = self.postal_cost
        return '%s' % formatprice.format_price(postal_cost)

    @property
    def discount_string(self):
        return '%s' % formatprice.format_price(self.get_discount())

    def get_bon_price(self):
        from aparnik.packages.shops.vouchers.models import Voucher
        return Voucher.objects.price_accessible_on_order(order=self)

    @property
    def bon_price_string(self):
        return '%s' % formatprice.format_price(self.get_bon_price())

    @property
    def bon_quantity(self):
        from aparnik.packages.shops.vouchers.models import Voucher
        return Voucher.objects.quantities_accessible_on_order(order=self)

    @property
    def total_dollar(self):
        dollar = 0
        for item in self.items.all():
            dollar = dollar + (item.dollar * item.quantity)

        return dollar

    @property
    def total_dollar_string(self):
        return '$%s' % self.total_dollar

    @property
    def total_count_item(self):
        x = 0
        for item in self.items.all():
            x = x + item.quantity
        return x

    @property
    def has_permit_use_wallet(self):
        for item in self.items.all():
            if not item.product_obj.has_permit_use_wallet:
                return False

        return True

    def add_item(self, product, quantity=1, description=''):
        item = None
        try:
            item = OrderItem.objects.get(
                order_obj=self,
                product_obj=product,
            )
            item.price = product.price
            item.quantity = quantity
            item.description = description
        except:
            item = OrderItem.objects.create(
                order_obj=self,
                product_obj=product,
                price=product.price,
                quantity=quantity,
                description=description
            )
        item.save()
        return item

    # TODO: check the coupon or all of the thing check need before pay
    def is_allow_to_pay(self):
        if self.coupon is not None:
            try:
                status = Coupon.objects.status(code=self.coupon.code, user=self.user, order=self)
                if status == Coupon.COUPON_STATUS_OK:
                    return True
                return False
            except:
                return False
        else:
            return True

    def pay_success(self, status=None):
        wallet_id = Product.objects.get_wallet().id
        if not status:
            status = Order.STATUS_PAID

        self.status = status

        if self.coupon is not None:
            self.coupon.redeem(user=self.user)

        for item in self.items.all():
            if item.product_obj.id == wallet_id:
                self.user.wallet = self.user.wallet + (item.product_obj.price * item.quantity)
                self.user.save()
            item.product_obj.get_real_instance().buy_success(order=self)

        self.postal_cost_value = Setting.objects.get(key='POSTAL_COST').get_value()

        self.save()

        NotificationForSingleUser.objects.send_notification(
            users=[self.user], type=Notification.NOTIFICATION_SUCCESS,
            title='خرید شما با موفقیت انجام شد.',
            description='فاکتور خرید شما به مبلغ %s با موفقیت پرداخت گردید.' % self.total_cost_string,
            model_obj=self,
        )

    def cancel(self):
        self.status = Order.STATUS_CANCEL
        self.save()

    @property
    def is_success(self):
        if self.status == Order.STATUS_COMPLETE or self.status == Order.STATUS_PAID or self.status == Order.STATUS_PAID_BY_WEBSITE:
            return True
        return False

    @property
    def earn_bon_if_buy(self):
        earn_bon = 0
        for item in self.items.all():
            earn_bon += item.product_obj.aparnik_bon_return * item.quantity
        return earn_bon

    @property
    def earn_bon_if_buy_value(self):
        price = round(self.earn_bon_if_buy * Setting.objects.get(key='APARNIK_BON_VALUE').get_value())
        return price

    @property
    def earn_bon_if_buy_value_string(self):
        price = self.earn_bon_if_buy_value
        return '%s' % formatprice.format_price(price)


def post_save_order_receiver(sender, instance, created, *args, **kwargs):
    from aparnik.packages.shops.vouchers.models import Voucher
    Voucher.objects.change_order(instance)

    from aparnik.packages.shops.cosales.models import CoSale
    CoSale.objects.change_order(order=instance)


post_save.connect(post_save_order_receiver, sender=Order)


class OrderItemManager(BaseModelManager):

    def get_queryset(self):
        return super(OrderItemManager, self).get_queryset()

    def get_this_user(self, user):
        if not user.is_authenticated:
            return OrderItem.objects.none()
        return self.get_queryset().filter(order_obj__user=user)


class OrderItem(BaseModel):
    order_obj = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_('Order'))
    product_obj = models.ForeignKey(Product, related_name='orderitem_set', on_delete=models.CASCADE,
                                    verbose_name=_('Product'))
    price = PriceField(big=True, verbose_name=_('Price'))
    is_tax = models.BooleanField(default=False, verbose_name=_('Is Tax'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Quantity'))
    description = models.TextField(default='', blank=True, null=True, verbose_name=_('Description'))

    objects = OrderItemManager()

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):

        return self.price_total_without_tax + self.price_tax_total

    def get_api_remove_item_uri(self):
        return reverse('aparnik-api:shops:orders:remove-item', args=[self.order_obj.id, self.id])

    @property
    def price_string(self):
        return '%s' % formatprice.format_price(self.price)

    @property
    def price_total_without_tax(self):
        if self.order_obj.status == Order.STATUS_WAITING and self.price != self.product_obj.price:
            self.price = self.product_obj.price
            self.save()

        if self.order_obj.status == Order.STATUS_WAITING and self.is_tax != self.product_obj.is_tax:
            self.is_tax = self.product_obj.is_tax
            self.save()
        price = self.price * self.quantity
        return price

    @property
    def price_total_without_tax_string(self):
        return '%s' % formatprice.format_price(self.price_total_without_tax)

    @property
    def price_complications(self):
        if self.is_tax:
            return round(self.price_total_without_tax * (3 / Decimal('100')))
        return 0

    @property
    def price_complications_string(self):
        return '%s' % formatprice.format_price(self.price_complications)

    @property
    def price_tax(self):
        if self.is_tax:
            return round(self.price_total_without_tax * (6 / Decimal('100')))
        return 0

    @property
    def price_tax_string(self):
        return '%s' % formatprice.format_price(self.price_tax)

    @property
    def price_tax_total(self):
        if self.is_tax:
            return self.price_tax + self.price_complications
        return 0

    @property
    def price_tax_total_string(self):
        return '%s' % formatprice.format_price(self.price_tax_total)

    @property
    def price_total_string(self):
        return '%s' % formatprice.format_price(self.get_cost())

    @property
    def dollar(self):
        return self.product_obj.price_fabric if self.product_obj.currency == Product.CURRENCY_DOLLAR else 0

    @property
    def dollar_string(self):
        return '$%s' % self.dollar

    @property
    def aparnik_bon_return(self):
        return int(self.product_obj.aparnik_bon_return * self.quantity)

    @property
    def maximum_use_aparnik_bon(self):
        return int(self.product_obj.maximum_use_aparnik_bon * self.quantity)

    class Meta:
        ordering = ('created_at',)
        verbose_name = _('OrderItem')
        verbose_name_plural = _('OrderItems')
