from django.urls import reverse
from rest_framework import serializers

from aparnik.packages.shops.products.api.serializers import ProductListSerializer, ProductDetailSerializer
from ..models import Subscription


class SubscriptionListSerializer(ProductListSerializer):

    class Meta:
        model = Subscription
        fields = ProductListSerializer.Meta.fields + [
            'type',
            'duration',
            'description',
        ]


class SubscriptionDetailSerializer(SubscriptionListSerializer, ProductDetailSerializer):

    class Meta:
        model = Subscription
        fields = SubscriptionListSerializer.Meta.fields + ProductDetailSerializer.Meta.fields + [

        ]
