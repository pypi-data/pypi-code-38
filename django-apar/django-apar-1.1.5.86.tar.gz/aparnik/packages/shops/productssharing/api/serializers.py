from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from aparnik.contrib.basemodels.api.serializers import BaseModelListSerializer, BaseModelDetailSerializer, ModelListPolymorphicSerializer
from aparnik.settings import aparnik_settings
from ..models import ProductSharing


UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER


class ProductSharingListSerializer(BaseModelListSerializer):
    user_product_share_with = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    url_products_sharing_set = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ProductSharingListSerializer, self).__init__(*args, **kwargs)

        # if 'context' in kwargs:
        # self.fields['notification_type'] = NotificationTypeDetailSerializer(read_only=True, context=kwargs['context'])

    class Meta:
        model = ProductSharing
        fields = BaseModelListSerializer.Meta.fields + [
            'user_product_share_with',
            'product',
            'update_at',
            'url_products_sharing_set',
        ]

    def get_user_product_share_with(self, obj):
        return UserSummeryListSerializer(obj.user_product_share_with_obj, many=False, read_only=True, context=self.context).data

    def get_product(self, obj):
        return ModelListPolymorphicSerializer(obj.product_obj, many=False, read_only=True, context=self.context).data

    def get_url_products_sharing_set(self, obj):
        return self.context['request'].build_absolute_uri(obj.product_obj.get_api_product_sharing_add_uri())


# ProductShare details
class ProductSharingDetailsSerializers(ProductSharingListSerializer, BaseModelDetailSerializer):
    # user_obj = serializers.SerializerMethodField()
    # shared_user_obj = serializers.SerializerMethodField()
    # shared_user_obj_id = serializers.CharField(max_length=20, required=True, write_only=True)
    # product_obj_id = serializers.IntegerField(required=True, write_only=True)
    # is_active = serializers.NullBooleanField()

    def __init__(self, *args, **kwargs):
        super(ProductSharingDetailsSerializers, self).__init__(*args, **kwargs)

    class Meta:
        model = ProductSharing
        fields = ProductSharingListSerializer.Meta.fields + BaseModelDetailSerializer.Meta.fields + [
            # 'user_obj',
            # 'shared_user_obj',
            # 'shared_user_obj_id',
            # 'product_obj_id',
        ]


# ProductShare List Polymorphic
class ProductSharingListPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            ProductSharing: ProductSharingListSerializer,
        }
        super(ProductSharingListPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}


# Teacher Details Polymorphic
class ProductSharingDetailsPolymorphicSerializer(PolymorphicSerializer):

    def __init__(self, *args, **kwargs):
        self.model_serializer_mapping = {
            ProductSharing: ProductSharingDetailsSerializers,
        }
        super(ProductSharingDetailsPolymorphicSerializer, self).__init__(*args, **kwargs)

    model_serializer_mapping = {}