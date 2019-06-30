from rest_framework import serializers

from aparnik.contrib.basemodels.api.admin.serializers import BaseModelAdminSerializer
from aparnik.packages.shops.orders.models import Order


class OrderAdminListSerializer(BaseModelAdminSerializer):


    def __init__(self, *args, **kwargs):
        super(OrderAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Order
        fields = BaseModelAdminSerializer.Meta.fields + [
        ]

        read_only_fields = BaseModelAdminSerializer.Meta.read_only_fields + [
        ]

