from rest_framework import serializers

from aparnik.contrib.basemodels.api.admin.serializers import BaseModelAdminSerializer


from aparnik.packages.shops.coupons.models import Coupon


class CouponAdminListSerializer(BaseModelAdminSerializer):


    def __init__(self, *args, **kwargs):
        super(CouponAdminListSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Coupon
        fields = BaseModelAdminSerializer.Meta.fields + [
            'code'
        ]

        read_only_fields = BaseModelAdminSerializer.Meta.read_only_fields + [

        ]
