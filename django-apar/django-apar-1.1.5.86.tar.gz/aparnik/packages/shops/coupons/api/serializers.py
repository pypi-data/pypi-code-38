# from rest_framework import serializers
# from aparnik.api.serializers import ModelSerializer
# from coupons.models import Coupon
#
# class CouponSummarySerializer(ModelSerializer):
#
#     discount = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Coupon
#         fields = [
#             'discount',
#         ]
#
#     def get_url(self, obj):
#         return self.context['request'].build_absolute_uri(obj.get_api_uri())
#
#     def get_total_cost(self, obj):
#         return obj.get_total_cost()
#
#     def get_total_cost_order(self, obj):
#         return obj.get_total_cost_order()
#
#     def get_url_request_pay(self, obj):
#         return self.context['request'].build_absolute_uri(obj.get_api_request_pay_uri())
#
#     def get_title(self, obj):
#         item = obj.items.first()
#         if item:
#             return item.product_obj.title
#         return ""
#
#     def get_discount(self, obj):
#         return obj.get_discount()