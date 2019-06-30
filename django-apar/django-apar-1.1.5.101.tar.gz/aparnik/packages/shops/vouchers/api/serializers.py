from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer, ModelListPolymorphicSerializer
from ..models import Voucher


class VoucherListSerializer(BaseModelListSerializer):

    def __init__(self, *args, **kwargs):
        super(VoucherListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = Voucher
        fields = BaseModelListSerializer.Meta.fields + [
            'quantity',
            'expire_at',
            'is_active',
            'is_spent',
            'price',
            'price_string',
        ]


# ProductShare details
class VoucherDetailsSerializers(VoucherListSerializer, BaseModelDetailSerializer):

    def __init__(self, *args, **kwargs):
        super(VoucherDetailsSerializers, self).__init__(*args, **kwargs)

    class Meta:
        model = Voucher
        fields = VoucherListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [

        ]
