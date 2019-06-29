from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import ( AllowAny, IsAuthenticated )
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from ..models import Coupon
from aparnik.packages.shops.orders.models import Order
from aparnik.packages.shops.orders.api.serializers import OrderSummarySerializer


class CouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'success': False,
            'msg': '',
            'data': {
            },
        }
        coupon_code = self.request.data.get('coupon_code', None)
        order = get_object_or_404(Order.objects.get_this_user(user=user), id=id)

        try:

            if not coupon_code:
                raise ValidationError({'coupon_code': [_('This field is required.')]})

            # payment = Payment.objects.request_pay(order=order, method=method, call_back_url=call_back_url, user=user)
            coupon = Coupon.objects.add_coupon(code=coupon_code, user=user, order=order)
            order.coupon = coupon
            order.save()
            content['data']['order'] = OrderSummarySerializer(order, many=False, read_only=True, context={'request': self.request}).data
            content['success'] = True
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))
