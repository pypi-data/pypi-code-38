# -*- coding: utf-8 -*-
from rest_framework import serializers
from zip_code_api.models import Address

class AddressListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
