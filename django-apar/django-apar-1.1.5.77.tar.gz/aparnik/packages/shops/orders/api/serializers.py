from rest_framework import serializers

from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer
from ..models import Order, OrderItem


class OrderSummarySerializer(BaseModelListSerializer):
    url_request_pay = serializers.SerializerMethodField()
    url_coupon = serializers.SerializerMethodField()
    url_add_address = serializers.SerializerMethodField()
    url_add_item = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    order_code = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    total_cost_order = serializers.SerializerMethodField()
    bon_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    has_permit_use_wallet = serializers.SerializerMethodField()
    earn_bon_if_buy = serializers.SerializerMethodField()
    earn_bon_if_buy_value = serializers.SerializerMethodField()
    earn_bon_if_buy_value_string = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = BaseModelListSerializer.Meta.fields + [
            'url_request_pay',
            'url_coupon',
            'url_add_address',
            'url_add_item',
            'address',
            'status',
            'is_success',
            'total_cost',
            'discount',
            'total_cost_order',
            'title',
            'order_code',
            'items_count',
            'postal_cost',
            'postal_cost_string',
            'discount_string',
            'total_cost_order_string',
            'total_cost_string',
            'bon_price_string',
            'bon_price',
            'bon_quantity',
            'has_permit_use_wallet',
            'earn_bon_if_buy',
            'earn_bon_if_buy_value',
            'earn_bon_if_buy_value_string',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
            'url_request_pay',
            'url_coupon',
            'url_add_item',
            'url_add_address',
            'address',
            'status',
            'is_success',
            'total_cost',
            'total_cost_order',
            'discount',
            'postal_cost',
            'postal_cost_string',
            'discount_string',
            'total_cost_order_string',
            'total_cost_string',
            'bon_price_string',
            'bon_price',
            'bon_quantity',
            'order_code',
            'items_count',
            'has_permit_use_wallet',
            'earn_bon_if_buy',
            'earn_bon_if_buy_value',
            'earn_bon_if_buy_value_string',
        ]

    def get_url_request_pay(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_request_pay_uri())

    def get_url_coupon(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_coupon_uri())

    def get_total_cost(self, obj):
        return obj.get_total_cost()

    def get_total_cost_order(self, obj):
        return obj.get_total_cost_order()

    def get_title(self, obj):
        item = obj.items.first()
        if item:
            return item.product_obj.title
        return ""

    def get_discount(self, obj):
        return obj.get_discount()

    def get_order_code(self, obj):
        return obj.order_code

    def get_bon_price(self, obj):
        return obj.get_bon_price()

    def get_url_add_address(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_add_address_uri())

    def get_url_add_item(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_add_item_uri())

    def get_address(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.address_obj, many=False, read_only=True, context=self.context).data if obj.address_obj else None

    def get_items_count(self, obj):
        return obj.items.count()

    def get_has_permit_use_wallet(self, obj):
        return obj.has_permit_use_wallet

    def get_earn_bon_if_buy(self, obj):
        return obj.earn_bon_if_buy

    def get_earn_bon_if_buy_value(self, obj):
        return obj.earn_bon_if_buy_value

    def get_earn_bon_if_buy_value_string(self, obj):
        return obj.earn_bon_if_buy_value_string


class OrderDetailSerializer(BaseModelDetailSerializer, OrderSummarySerializer):

    items = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(OrderDetailSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
            # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])


    class Meta:
        model = Order
        fields = OrderSummarySerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'items',
            'payments',
        ]

    def get_items(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelDetailsPolymorphicSerializer
        return ModelDetailsPolymorphicSerializer(obj.items, many=True, read_only=True, context=self.context).data

    def get_payments(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        return ModelListPolymorphicSerializer(obj.payments, many=True, read_only=True, context=self.context).data


class OrderItemDetailSerializer(BaseModelDetailSerializer):

    product = serializers.SerializerMethodField()
    url_remove_item = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(OrderItemDetailSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
            # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = OrderItem
        fields = BaseModelDetailSerializer.Meta.fields + [
            'product',
            'url_remove_item',
            'price',
            'quantity',
        ]
        read_only_fields = BaseModelDetailSerializer.Meta.read_only_fields + [
            'url_remove_item',
        ]

    def get_product(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelDetailsPolymorphicSerializer
        return ModelDetailsPolymorphicSerializer(obj.product_obj.get_real_instance(), many=False, read_only=True, context=self.context).data

    def get_url_remove_item(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_remove_item_uri())

