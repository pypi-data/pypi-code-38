# -*- coding: utf-8 -*-


from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError


from .serializers import ProductSharingListSerializer
from ..models import ProductSharing


class ProductSharingListAPIView(ListAPIView):
    serializer_class = ProductSharingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = ProductSharing.objects.share_this_user(user)
        if 'product_id' in self.request.parser_context['kwargs']:
            product_id = self.request.parser_context['kwargs']['product_id']
            queryset = ProductSharing.objects.share_this_user(user, product_id)
        return queryset


class ProductSharingSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        content = {
            'is_shared': False,
        }
        user = self.request.user
        from aparnik.packages.shops.products.models import Product
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user_product_share_with = get_object_or_404(User, sys_id=self.request.data.get('user_product_share_with_id', None))

        product_obj = get_object_or_404(Product.objects.all(), id=product_id)

        try:
            obj = get_object_or_404(ProductSharing.objects.filter(product_obj=product_obj), user_obj=user,
                                    user_product_share_with_obj=user_product_share_with)
            obj.is_active = not obj.is_active
            obj.save()
            content['is_shared'] = obj.is_active
            status = HTTP_200_OK

        except Exception as e:
            try:

                obj = ProductSharing.objects.create(user_obj=user, product_obj=product_obj,
                                                    user_product_share_with_obj=user_product_share_with,
                                                    is_active=True)
                content['is_shared'] = obj.is_active
                status = HTTP_200_OK
            except Exception as e:
                raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)
