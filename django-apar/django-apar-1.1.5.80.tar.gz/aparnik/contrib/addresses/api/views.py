# -*- coding: utf-8 -*-


from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from .serializers import AddressDetailSerializer
from ..models import UserAddress


class AddressListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserAddress.objects.this_user(user)


class AddressCreateAPIView(CreateAPIView):
    serializer_class = AddressDetailSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user_obj=user)


class AddressSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, model_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'is_default': False,
        }

        try:
            address = get_object_or_404(UserAddress.objects.all(), id=model_id)
            content['is_default'] = address.set_is_default(user)
            status = HTTP_200_OK

        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)
