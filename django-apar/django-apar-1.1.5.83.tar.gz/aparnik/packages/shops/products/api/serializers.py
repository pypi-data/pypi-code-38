# -*- coding: utf-8 -*-


from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from aparnik.settings import Setting
from aparnik.api.serializers import ModelSerializer
from aparnik.utils.utils import is_app_installed
from aparnik.contrib.filefields.api.serializers import FileFieldListSerailizer
from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer
from aparnik.contrib.segments.api.serializers import BaseSegmentListPolymorphicSerializer
from ..models import Product, ProductPropertyMembership


# Product Details Serializer
class ProductPropertyMembershipListSerializer(ModelSerializer):
    title = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = ProductPropertyMembership
        fields = [
            'id',
            'title',
            'value',
            'icon',
        ]

    def get_title(self, obj):
        return obj.property.title

    def get_icon(self, obj):
        return FileFieldListSerailizer(obj.property.icon, many=False, read_only=True, context=self.context).data


class ProductListSerializer(BaseModelDetailSerializer):
    is_buy = serializers.SerializerMethodField()
    has_permit = serializers.SerializerMethodField()
    is_user_invited = serializers.SerializerMethodField()
    price_string = serializers.SerializerMethodField()
    is_discount_percent_expire_show = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ProductListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Product
        fields = BaseModelDetailSerializer.Meta.fields + [
            'title',
            'price',
            'is_buy',
            'is_free',
            'is_user_invited',
            'has_permit',
            'price_fabric',
            'discount_percent',
            'delivery_type',
            'price_fabric_string',
            'price_string',


            'is_discount_percent_expire_show',
            'discount_percent_expire',
            'is_subscription',
        ]
        # TODO: fix read only fields
        read_only_fields = BaseModelDetailSerializer.Meta.read_only_fields + [
            'is_discount_percent_expire_show',
            'is_subscription',
            'is_buy',
            'has_permit',
            'is_user_invited',
            'price_string',
            'is_discount_percent_expire_show',
            'is_free'
        ]

    def get_is_buy(self, obj):
        return obj.is_buy(self.context['request'].user)

    # Is user eligible to use this product(purchased, free or shared product returns True)
    def get_has_permit(self, obj):
        user = self.context['request'].user
        return obj.has_permit(user=user)

    # Determines if a product shared with this user.
    def get_is_user_invited(self, obj):
        user = self.context['request'].user
        return obj.is_user_invited(user=user)

    def get_price_string(self, obj):
        user = self.context['request'].user
        return obj.price_string_description(user=user)

    def get_is_discount_percent_expire_show(self, obj):
        return obj.discount_percent > 0


# Product Details Serializer
class ProductDetailSerializer(ProductListSerializer):
    slider_segment = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    url_products_sharing = serializers.SerializerMethodField()
    url_products_sharing_set = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ProductDetailSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Product
        fields = ProductListSerializer.Meta.fields + [
            'slider_segment',
            'properties',
            'further_details',
            'url_products_sharing',
            'url_products_sharing_set',
            'aparnik_bon_return',
            'aparnik_bon_return_value_string',
            'aparnik_bon_return_expire_date',
            'maximum_use_aparnik_bon',
            'has_permit_use_wallet',
        ]

        read_only_fields = ProductListSerializer.Meta.read_only_fields + ['slider_segment',
                                                                          'properties',
                                                                          'url_products_sharing',
                                                                          'url_products_sharing_set']

    def get_slider_segment(self, obj):
        return BaseSegmentListPolymorphicSerializer(obj.slider_segment_obj, many=False, read_only=True, context=self.context).data

    def get_properties(self, obj):
        return ProductPropertyMembershipListSerializer(obj.productpropertymembership_set.all(), many=True, read_only=True, context=self.context).data

    def get_url_products_sharing(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_products_sharing_uri())

    def get_url_products_sharing_set(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_product_sharing_add_uri())


# Product List Polymorphic
class ProductListPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        model_serializer_mapping = {
            Product: ProductListSerializer,
        }

        # Course
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.packages.educations.courses.models import Course
            from aparnik.packages.educations.courses.api.serializers import BaseCourseListPolymorphicSerializer
            model_serializer_mapping[Course] = BaseCourseListPolymorphicSerializer

        # File
        if is_app_installed('aparnik.packages.shops.files'):
            from aparnik.packages.shops.files.models import File
            from aparnik.packages.shops.files.api.serializers import FileListPolymorphicSerializer
            model_serializer_mapping[File] = FileListPolymorphicSerializer

        # Subscription
        if is_app_installed('aparnik.packages.shops.subscriptions'):
            from aparnik.packages.shops.subscriptions.models import Subscription
            from aparnik.packages.shops.subscriptions.api.serializers import SubscriptionListSerializer
            model_serializer_mapping[Subscription] = SubscriptionListSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(ProductListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Product Details Polymorphic
class ProductDetailsPolymorphicSerializer(PolymorphicSerializer):
    def __init__(self, *args, **kwargs):
        model_serializer_mapping = {
            Product: ProductDetailSerializer,
        }

        # Course
        if is_app_installed('aparnik.packages.educations.courses'):
            from aparnik.packages.educations.courses.models import Course
            from aparnik.packages.educations.courses.api.serializers import BaseCourseDetailsPolymorphicSerializer
            model_serializer_mapping[Course] = BaseCourseDetailsPolymorphicSerializer

        # File
        if is_app_installed('aparnik.packages.shops.files'):
            from aparnik.packages.shops.files.models import File
            from aparnik.packages.shops.files.api.serializers import FileDetailsPolymorphicSerializer
            model_serializer_mapping[File] = FileDetailsPolymorphicSerializer

        # Subscription
        if is_app_installed('aparnik.packages.shops.subscriptions'):
            from aparnik.packages.shops.subscriptions.models import Subscription
            from aparnik.packages.shops.subscriptions.api.serializers import SubscriptionDetailSerializer
            model_serializer_mapping[Subscription] = SubscriptionDetailSerializer

        self.model_serializer_mapping = model_serializer_mapping
        super(ProductDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}
