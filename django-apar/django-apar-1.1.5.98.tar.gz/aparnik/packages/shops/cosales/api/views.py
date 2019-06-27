from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError
from aparnik.contrib.users.models import User
from .serializers import CoSaleUserListSerializer, CoSaleListSerializer
from ..models import CoSale


class CoSaleUserListAPIView(ListAPIView):
    serializer_class = CoSaleUserListSerializer
    permission_classes = [IsAuthenticated]

    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        user = self.request.user
        return [user]


class CoSaleListAPIView(ListAPIView):
    serializer_class = CoSaleListSerializer
    permission_classes = [IsAuthenticated]

    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        user = self.request.user
        return CoSale.objects.this_user(user)


# class OrderDetailAPIView(RetrieveAPIView):
#     serializer_class = OrderDetailSerializer
#     permission_classes = [IsAuthenticated]
#     lookup_url_kwarg = 'id'
#     lookup_field = 'id'
#
#     def get_queryset(self):
#         user = self.request.user
#
#         return Order.objects.get_this_user(user=user)
#
#
# class AddProductOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, id=None, format=None, *args, **kwargs):
#         status = HTTP_400_BAD_REQUEST
#         user = self.request.user
#         # id = product_id
#         content = {
#             'success': False,
#             'msg': '',
#             'data': {
#             },
#         }
#         order = None
#         products = None
#         products_id = request.POST.get('products_id').split(',')
#         try:
#             products = Product.objects.filter(id__in=products_id)
#             if id:
#                 order = get_object_or_404(Order.objects.all(), id=id)
#             else:
#                 order = Order.objects.create(user=user)
#         except Exception as e:
#             content["msg"] = e
#             content["success"] = False
#             content["data"] = {}
#             return Response(content, status=status)
#
#         for product in products.all():
#             order.add_item(product=product)
#
#         order.save()
#
#         content['data']['order'] = OrderSummarySerializer(order, many=False, read_only=True,
#                                                           context={'request': self.request}).data
#         content['success'] = True
#         status = HTTP_200_OK
#         return Response(content, status=status)
