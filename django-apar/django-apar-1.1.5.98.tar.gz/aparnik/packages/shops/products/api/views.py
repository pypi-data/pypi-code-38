# -*- coding: utf-8 -*-


from django.db.models import Count, Q
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView

from aparnik.packages.shops.orders.models import Order
from aparnik.contrib.basemodels.api.views import BaseModelSortAPIView
from .serializers import ProductListSerializer
from ..models import Product


class ProductSortAPIView(BaseModelSortAPIView):
    permission_classes = [AllowAny]

    """
        A view that returns the count of active users in JSON.
        """
    def __init__(self, *args, **kwargs):
        super(ProductSortAPIView, self).__init__(*args, **kwargs)
        command_dict = {
            'buy_count': {
                'label': 'تعداد خرید',
                'queryset_filter': Q(),
                'annotate_command': {'count': Count('orderitem_set__order_obj', filter=Order.query_success('orderitem_set__order_obj'))},
                'key_sort': 'count',
            },
            'my_products': {
                'label': 'محصولات من',
                'queryset_filter': Q(),
                'annotate_command': {},
                'key_sort': 'my_product_count',
            }
        }

        self.command_dict.update(command_dict)


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # queryset = Product.objects.active(user=user)
        queryset = Product.objects.active(user=user)
        sort_api = ProductSortAPIView(request=self.request)
        queryset = sort_api.get_query_sort(queryset)
        return queryset
