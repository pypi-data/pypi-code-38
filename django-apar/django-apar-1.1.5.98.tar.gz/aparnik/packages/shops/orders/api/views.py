from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from aparnik.settings import Setting
from aparnik.utils.utils import convert_iran_phone_number_to_world_number
from aparnik.contrib.addresses.models import UserAddress
from aparnik.packages.shops.products.models import Product
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer, ModelDetailsPolymorphicSerializer
from ..models import Order

User = get_user_model()


class OrderListAPIView(ListAPIView):
    serializer_class = ModelDetailsPolymorphicSerializer
    permission_classes = [IsAuthenticated]

    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.get_this_user(user=user)

        return Order.objects.all()


class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = ModelDetailsPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user

        return Order.objects.get_this_user(user=user)


class AddProductOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user
        # id = product_id
        content = {
            'success': False,
            'msg': '',
            'data': {
            },
        }
        order = None
        products = None
        products_id = request.POST.get('products_id').split(',')
        quantity = request.POST.get('quantity', 1)
        try:
            products = Product.objects.filter(id__in=products_id)
            if id:
                order = get_object_or_404(Order.objects.all(), id=id)
            else:
                order = Order.objects.create(user=user)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        for product in products.all():
            order.add_item(product=product, quantity=quantity)

        order.save()

        content['data']['order'] = ModelDetailsPolymorphicSerializer(order, many=False, read_only=True,
                                                          context={'request': self.request}).data
        content['success'] = True
        status = HTTP_200_OK
        return Response(content, status=status)


class AddProductOrderByWebsitesAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, id=None, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        content = {

        }
        secret_key_post = request.POST.get('secret_key', None)
        secret_key = get_object_or_404(Setting.objects.active(), key='SECRET_KEY').get_value()
        if secret_key != secret_key_post:
            raise ValidationError({
                'non_fields_error': _("Bad Request.")
            })
        username = request.POST.get('username', None)
        if username:
            username = convert_iran_phone_number_to_world_number(username)
        try:
            user = User.objects.get(username=username)
        except:
            user = User.objects.create(username=username)

        self.request.user = user
        order = None
        products = None
        products_id = request.POST.get('products_id').split(',')

        quantity = request.POST.get('quantity', 1)

        try:
            products = Product.objects.filter(id__in=products_id)
            if id:
                order = get_object_or_404(Order.objects.all(), id=id)
            else:
                order = Order.objects.create(user=user)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        for product in products.all():
            order.add_item(product=product, quantity=quantity)

        order.is_sync_with_websites = True
        order.save()
        order.pay_success(status=Order.STATUS_PAID_BY_WEBSITE)
        content = ModelDetailsPolymorphicSerializer(order, many=False, read_only=True,
                                                                     context={'request': self.request}).data
        status = HTTP_200_OK
        return Response(content, status=status)


class RemoveProductOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, item_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user
        # id = product_id
        content = {

        }
        order = None

        try:
            from ..models import OrderItem
            order = get_object_or_404(Order.objects.all(), id=id)
            item = get_object_or_404(OrderItem.objects.all(), id=item_id)
            if order.is_success:
                raise ValidationError({
                    'order': _("This order finish before.")
                })
            item.delete()
        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        order.save()

        content = ModelDetailsPolymorphicSerializer(order, many=False, read_only=True,
                                                          context={'request': self.request}).data
        status = HTTP_200_OK
        return Response(content, status=status)


class ChargeWalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user
        # id = product_id
        content = {
            'success': False,
            'msg': '',
            'data': {
            },
        }
        order = None
        product = Product.objects.get_wallet()
        count = request.POST.get('toman', 10)
        try:
            order = Order.objects.create(user=user)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        order.add_item(product=product, quantity=count)

        order.save()

        content['data']['order'] = ModelDetailsPolymorphicSerializer(order, many=False, read_only=True,
                                                          context={'request': self.request}).data
        content['success'] = True
        status = HTTP_200_OK
        return Response(content, status=status)


class AddOrderAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = self.request.user
        address_id = self.request.data.get('address_id', None)

        user_address = get_object_or_404(UserAddress.objects.active(), id=address_id, user_obj=user)
        order = get_object_or_404(Order.objects.active(), id=id, user=user)

        try:
            order.address_obj = user_address
            order.save()

            content = ModelDetailsPolymorphicSerializer(order,
                                                     many=False, read_only=True,
                                                     context={'request': self.request}).data
            status = HTTP_200_OK
            return Response(content, status=status)

        except Exception as e:
            raise ValidationError(as_serializer_error(e))
