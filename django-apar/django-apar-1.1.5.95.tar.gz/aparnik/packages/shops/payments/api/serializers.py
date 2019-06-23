from django.urls import reverse
from rest_framework import serializers

from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer
from ..models import Payment


class PaymentSummarySerializer(BaseModelListSerializer):
    date = serializers.SerializerMethodField()
    method = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = BaseModelListSerializer.Meta.fields + [
            'date',
            'method',
            'bank_reference',
            'status',
            'uuid',
        ]

    def get_date(self, obj):

        return obj.update_at if obj.update_at else obj.created_at

    def get_method(self, obj):

        return obj.get_method_json_display()


    # request.build_absolute_uri(payment.get_url())

class PaymentDetailSerializer(BaseModelDetailSerializer, PaymentSummarySerializer):

    url_pay = serializers.SerializerMethodField()
    url_pay_cancel = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    method = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = PaymentSummarySerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            'url_pay',
            'url_pay_cancel',
            'date',
            'method',
            'bank_reference',
            'status',
            'uuid',
            'order',
        ]

    def get_url_pay(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_url())

    def get_url_pay_cancel(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_pay_cancel_uri())

    def get_order(self, obj):
        from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
        order_summary = ModelListPolymorphicSerializer(obj.order_obj, many=False, read_only=True, context=self.context)
        return order_summary.data
