# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from rest_framework import serializers
import datetime
from aparnik.api.serializers import ModelSerializer
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer, ModelListPolymorphicSerializer
from aparnik.packages.shops.cosales.models import CoSale
from aparnik.contrib.users.api.serializers import UserSummaryListSerializer

User = get_user_model()


class CoSaleUserListSerializer(ModelSerializer):
    id = serializers.SerializerMethodField()
    transaction_today_count = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    user_subset_count = serializers.SerializerMethodField()
    today_earnings = serializers.SerializerMethodField()
    today_earnings_string = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    earning_invited_by = serializers.SerializerMethodField()
    earning_invited_by_string = serializers.SerializerMethodField()
    order_complete_count = serializers.SerializerMethodField()
    url_ios_app = serializers.SerializerMethodField()
    url_android_app = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'transaction_today_count',
            'user_subset_count',
            'summary',
            'today_earnings',
            'today_earnings_string',
            'user',
            # درآمد کسی که دعوت کرده
            'earning_invited_by',
            'earning_invited_by_string',
            'order_complete_count',
            'url_ios_app',
            'url_android_app',
            'resourcetype',
        ]

        read_only_fields = [
            'id',
            'transaction_today_count',
            'summary',
            'user_subset_count',
            'today_earnings',
            'today_earnings_string',
            'user',
            # درآمد کسی که دعوت کرده
            'earning_invited_by',
            'earning_invited_by_string',
            'order_complete_count',
            'url_ios_app',
            'url_android_app',
            'resourcetype',
        ]

    def get_id(self, obj):
        return obj.sys_id

    def get_transaction_today_count(self, obj):
        return CoSale.objects.history(user=obj, is_user_bought=False).count()

    def get_summary(self, obj):
        return obj.co_sale_summary

    def get_today_earnings(self, obj):
        return CoSale.objects.transaction_price(user=obj, is_user_bought=False)

    def get_today_earnings_string(self, obj):
        return CoSale.objects.transaction_price_string(user=obj, is_user_bought=False)

    def get_user(self, obj):
        return UserSummaryListSerializer(obj, many=False, read_only=True, context=self.context).data

    def get_user_subset_count(self, obj):
        return '%s' % obj.invite_by.get_invited_by().count()

    def get_earning_invited_by(self, obj):
        return CoSale.objects.transaction_price(user=obj, is_user_bought=True, start_date=datetime.datetime(100, 12, 31, 23, 59, 59))

    def get_earning_invited_by_string(self, obj):
        return CoSale.objects.transaction_price_string(user=obj, is_user_bought=True, start_date=datetime.datetime(100, 12, 31, 23, 59, 59))

    def get_order_complete_count(self, obj):
        return CoSale.objects.history(user=obj, is_user_bought=True, start_date=datetime.datetime(100, 12, 31, 23, 59, 59)).count()

    def get_url_ios_app(self, obj):
        # TODO: fix link
        return self.context['request'].build_absolute_uri('ios')

    def get_url_android_app(self, obj):
        # TODO: fix link
        return self.context['request'].build_absolute_uri('android')

    def get_resourcetype(self, obj):
        return 'CoSaleUser'


class CoSaleListSerializer(BaseModelListSerializer):
    user_bought = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = CoSale
        fields = BaseModelListSerializer.Meta.fields + [
            'price',
            'price_string',
            'user_bought',
            'order',
            'created_at',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
            'price',
            'price_string',
            'user_bought',
            'order',
            'created_at',
        ]

    def get_user_bought(self, obj):
        return UserSummaryListSerializer(obj.user_bought_obj, many=False, read_only=True, context=self.context).data

    def get_order(self, obj):
        return ModelListPolymorphicSerializer(obj.order_obj, many=False, read_only=True, context=self.context).data


class CoSaleDetailsSerializer(BaseModelDetailSerializer, CoSaleListSerializer):

    def __init__(self, *args, **kwargs):
        super(CoSaleDetailsSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = CoSale
        fields = CoSaleListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [

        ]

        read_only_fields = CoSaleListSerializer.Meta.read_only_fields + BaseModelListSerializer.Meta.read_only_fields + [

        ]
