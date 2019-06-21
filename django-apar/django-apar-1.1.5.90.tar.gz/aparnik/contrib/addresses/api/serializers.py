from django.urls import reverse
from rest_framework import serializers

from aparnik.contrib.basemodels.api.serializers import BaseModelDetailSerializer, BaseModelListSerializer
from aparnik.contrib.province.api.serializers import CityDetailSerializer
from ..models import UserAddress


# Address List Serializer
class AddressListSerializer(BaseModelListSerializer):

    url_set_default = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(AddressListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = UserAddress
        fields = BaseModelListSerializer.Meta.fields + [
            'city',
            'address',
            'postal_code',
            'phone',
            'is_default',
            'url_set_default',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + [
            'city',
            'url_set_default',
            'is_default',
        ]

    def get_city(self, obj):
        return None if not obj.city_obj else CityDetailSerializer(obj.city_obj, many=False, read_only=True, context=self.context).data

    def get_url_set_default(self, obj):
        return self.context['request'].build_absolute_uri(reverse('aparnik-api:addresses:set', args=[obj.id]))


# Address Details Serializer
class AddressDetailSerializer(BaseModelDetailSerializer, AddressListSerializer):
    city_obj_id = serializers.IntegerField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super(AddressDetailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = UserAddress
        fields = BaseModelDetailSerializer.Meta.fields + AddressListSerializer.Meta.fields + [
            'city_obj_id',
        ]

        read_only_fields = BaseModelListSerializer.Meta.read_only_fields + AddressListSerializer.Meta.read_only_fields + []
