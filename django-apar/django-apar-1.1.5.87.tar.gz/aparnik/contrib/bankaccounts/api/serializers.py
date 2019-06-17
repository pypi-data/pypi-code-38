from django.urls import reverse
from rest_framework import serializers

from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer, ModelListPolymorphicSerializer
from aparnik.contrib.province.api.serializers import CityDetailSerializer
from ..models import BankAccount, BankName


# List Serializer
class BankNameListSerializer(BaseModelListSerializer):

    def __init__(self, *args, **kwargs):
        super(BankNameListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BankName
        fields = BaseModelListSerializer.Meta.fields + [
            'title',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
        ]


# Details Serializer
class BankNameDetailSerializer(BaseModelDetailSerializer, BankNameListSerializer):

    def __init__(self, *args, **kwargs):
        super(BankNameDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BankName
        fields = BaseModelDetailSerializer.Meta.fields + BankNameListSerializer.Meta.fields + [
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + BankNameListSerializer.Meta.read_only_fields + []


class BankAccountListSerializer(BaseModelListSerializer):

    bank_name = serializers.SerializerMethodField()
    url_set_default = serializers.SerializerMethodField()
    url_update = serializers.SerializerMethodField()
    resourcetype = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(BankAccountListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BankAccount
        fields = BaseModelListSerializer.Meta.fields + [
            'url_update',
            'bank_name',
            'account_number',
            'shaba_number',
            'card_number',
            'is_default',
            'url_set_default',
            'resourcetype'
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
            'url_update',
            'bank_name',
            'is_default',
            'url_set_default',
            'resourcetype'
        ]

    def get_url_update(self, obj):
        return self.context['request'].build_absolute_uri(reverse('aparnik-api:bankaccounts:update', args=[obj.id]))

    def get_bank_name(self, obj):
        return ModelListPolymorphicSerializer(obj.bank_name_obj, many=False, read_only=True, context=self.context).data

    def get_url_set_default(self, obj):
        return self.context['request'].build_absolute_uri(reverse('aparnik-api:bankaccounts:set', args=[obj.id]))

    def get_resourcetype(self, obj):
        return 'BankAccount'


# Details Serializer
class BankAccountDetailSerializer(BaseModelDetailSerializer, BankAccountListSerializer):
    bank_name_obj_id = serializers.IntegerField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super(BankAccountDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = BankAccount
        fields = BaseModelDetailSerializer.Meta.fields + BankAccountListSerializer.Meta.fields + [
            'bank_name_obj_id',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + BankAccountListSerializer.Meta.read_only_fields + []
