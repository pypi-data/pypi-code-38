# -*- coding: utf-8 -*-


from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError

from aparnik.contrib.basemodels.models import BaseModel
from .serializers import NotifyMeListSerializer
from ..models import NotifyMe


class NotifyMeListAPIView(ListAPIView):
    serializer_class = NotifyMeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = NotifyMe.objects.this_user(user)
        # if 'model' in self.request.parser_context['kwargs']:
        #     product_id = self.request.parser_context['kwargs']['product_id']
        #     queryset = ProductSharing.objects.share_this_user(user, product_id)
        return queryset


class NotifyMeSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, model_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'is_notify': False,
        }

        model = get_object_or_404(BaseModel.objects.all(), id=model_id)

        try:
            obj = get_object_or_404(NotifyMe.objects.active().filter(model_obj=model), user_obj=user)
            obj.delete()
            status = HTTP_200_OK

        except Exception as e:
            try:
                obj = NotifyMe.objects.create(user_obj=user, model_obj=model, is_active=True)
                content['is_notify'] = True
                status = HTTP_200_OK
            except Exception as e:
                raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)
