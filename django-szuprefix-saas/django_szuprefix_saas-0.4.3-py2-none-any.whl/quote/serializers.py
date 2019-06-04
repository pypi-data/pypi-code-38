# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models, choices
from ..saas.mixins import PartySerializerMixin


class ManufacturerSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Manufacturer
        fields = ('name', 'code')


class CompanySerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ('name', 'code', 'is_vendor', 'is_customer')


class ProductSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    manufacturer_name = serializers.CharField(source="manufacturer.__str__", read_only=True)

    class Meta:
        model = models.Product
        fields = ('name', 'number', 'manufacturer', 'manufacturer_name', 'code')


class QuoteSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.__str__", label='供应商', read_only=True)
    product_name = serializers.CharField(source="product.__str__", label='产品', read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", label='人员', read_only=True)

    class Meta:
        model = models.Quote
        exclude = ()
        read_only_fields = ('amount', 'amount_taxed', 'delivery_days_from', 'delivery_days_to', 'party')


class ItemSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.__str__", label='产品', read_only=True)
    customer_name = serializers.CharField(source="customer.__str__", label='客户', read_only=True)
    user_name = serializers.CharField(source="request.user.__str__", label='用户', read_only=True)

    class Meta:
        model = models.Item
        fields = (
            'product', 'product_name', 'customer', 'customer_name', 'create_time', 'user_name', 'quantity',
            'unit_price', 'unit_price_taxed', 'amount', 'amount_taxed', 'memo', 'request',
            'party', 'delivery', 'delivery_days_from', 'delivery_days_to')
        read_only_fields = ('amount', 'amount_taxed', 'party', 'delivery_days_from', 'delivery_days_to')


class ItemSmallSerializer(ItemSerializer):
    class Meta(ItemSerializer.Meta):
        fields = ('product_name',)


class RequestSerializer(PartySerializerMixin, IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.__str__", label='客户', read_only=True)
    items_count = serializers.IntegerField(source="items.count", label="产品数量", read_only=True)
    items = ItemSmallSerializer(label="产品", read_only=True, many=True)
    user_name = serializers.CharField(source="user.get_full_name", label='销售', read_only=True)
    status_name = serializers.CharField(source="get_status_display", label='状态', read_only=True)

    class Meta:
        model = models.Request
        # exclude = ()
        read_only_fields = ('code', 'amount', 'amount_taxed', 'party')
        fields = (
            'customer', 'user', 'items', 'customer_name', 'amount', 'amount_taxed', 'items_count', 'create_time',
            'status', 'user_name', 'code', 'status', 'status_name'
        )
        # todo: 如果这里用exclude, 而不用fields, 那code会一直提示不能为空, 有空去深入研究一下差别


class RequestChangeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Request
        fields = ('id', 'status')

    def validate(self, data):
        o = self.instance
        dps = choices.PATHS_REQUEST_STATUS.get(o.status, [])
        status = data['status']
        if status not in dps:
            m = dict(choices.CHOICES_REQUEST_STATUS)
            raise serializers.ValidationError("状态转换不合规则:%s => %s " % (m.get(o.status), m.get(status)))
        return data

        # def save(self, **kwargs):
        #     # self.instance.status = self.
        #     super(RequestChangeStatusSerializer, self).save(**kwargs)
