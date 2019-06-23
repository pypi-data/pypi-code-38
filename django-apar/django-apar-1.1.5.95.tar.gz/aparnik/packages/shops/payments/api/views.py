from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.permissions import ( AllowAny, IsAuthenticated )
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from aparnik.packages.shops.orders.models import Order
from aparnik.contrib.basemodels.api.serializers import ModelDetailsPolymorphicSerializer
from ..models import Payment


class PayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'success': False,
            'msg': '',
            'data': {
                'url': '',
            },
        }

        call_back_url = self.request.data.get('call_back_url', None)
        method = self.request.data.get('method', None)
        order = get_object_or_404(Order.objects.get_this_user(user=user), id=id)

        try:

            if not call_back_url:
                content['msg'] += 'call back is required\n'

            if not method:
                content['msg'] += 'method is required\n'

            if content['msg']:
                raise ValidationError({'__all__': [_(content['msg'])]})

            # payment = Payment.objects.request_pay(transaction=transaction, method=method, call_back_url=call_back_url, user=user)
            payment = Payment.objects.request_pay(order=order, method=method, call_back_url=call_back_url, user=user)
            content['data']['payment'] = ModelDetailsPolymorphicSerializer(payment, many=False, read_only=True, context={'request': self.request}).data
            content['success'] = True
            status = HTTP_200_OK

        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)


class PaymentPayListAPIView(ListAPIView):
    serializer_class = ModelDetailsPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return Payment.objects.get_this_user(user=user)


class PaymentPayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'success': False,
            'msg': '',
            'data': {
                # 'last_wallet': user.wallet,
            },
        }

        payments_obj = get_list_or_404(Payment.objects.get_this_user(user=user).order_by('-id'), uuid=uuid)

        try:
            # check wallet money
            pay_obj = payments_obj[0]
            if not (pay_obj.method == pay_obj.METHOD_WALLET and pay_obj.order_obj.status == Payment.STATUS_WAITING and pay_obj.status == Payment.STATUS_WAITING):
                raise ValidationError()


            pay_success = pay_obj.success()
            # content['data']['wallet'] = user.wallet
            content["success"] = True
            status = HTTP_200_OK

        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)


class PaymentPayCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'success': False,
            'msg': '',
            'data': {
            },
        }

        payments_obj = get_list_or_404(Payment.objects.get_this_user(user=user).order_by('-id'), uuid=uuid)

        try:
            # check wallet money
            pay_obj = payments_obj[0]
            pay_success = pay_obj.cancel()
            # content['data']['wallet'] = user.wallet
            content["success"] = True
            status = HTTP_200_OK

        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)
