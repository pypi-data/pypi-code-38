from rest_framework import serializers

from aparnik.api.serializers import ModelSerializer
from aparnik.utils.utils import convert_iran_phone_number_to_world_number

from ..models import ContactUs


class ContactUsDestailSerializer(ModelSerializer):
    url = serializers.SerializerMethodField()
    phone = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ContactUsDestailSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = ContactUs
        fields = [
            'id',
            'url',
            'website',
            'address',
            'phone',
            'email',
            'first_name',
            'last_name',
            'title',
            'content',
            'is_active',
            'update_at',
        ]

        read_only_fields = [
            'id',
            'url',
            'is_active',
            'update_at',
        ]

    def get_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_api_uri())

    def validate_phone(self, value):
        return convert_iran_phone_number_to_world_number(value)
