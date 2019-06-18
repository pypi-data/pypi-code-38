# -*- coding: utf-8 -*-


from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from .serializers import VoucherListSerializer
from ..models import Voucher


class VoucherListAPIView(ListAPIView):
    serializer_class = VoucherListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Voucher.objects.this_user(user, only_accessible=False)
        # if 'product_id' in self.request.parser_context['kwargs']:
        #     product_id = self.request.parser_context['kwargs']['product_id']
        #     queryset = Voucher.objects.this_user(user, product_id)
        return queryset
