from rest_framework import serializers

from aparnik.contrib.basemodels.api.admin.serializers import BaseModelAdminSerializer


from aparnik.packages.shops.products.models import Product


class ProductAdminListSerializer(BaseModelAdminSerializer):

    def __init__(self, *args, **kwargs):
        super(ProductAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Product
        fields = BaseModelAdminSerializer.Meta.fields + [

            'title',

        ]

        read_only_fields = BaseModelAdminSerializer.Meta.read_only_fields + [

        ]