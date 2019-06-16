# -*- coding: utf-8 -*-


from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from ..models import Book, Publisher, WriterTranslator
from .serializers import PublisherListSerializer, PublisherDetailsSerializer, WriterTranslatorListSerializer, WriterTranslatorDetailsSerializer
from aparnik.packages.shops.products.api.serializers import ProductListPolymorphicSerializer


class BookListAPIView(ListAPIView):
    serializer_class = ProductListPolymorphicSerializer
    permission_classes = [AllowAny]
    queryset = Book.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)


class BookUserListAPIView(ListAPIView):
    serializer_class = ProductListPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        user = self.request.user
        from aparnik.packages.shops.orders.models import Order
        queryset = Book.objects.filter(
            id__in=Order.objects.get_this_user_bought(user=user, custom_type=Book).values_list('items__product_obj', flat=True))
        return queryset


class PublisherListAPIView(ListAPIView):
    serializer_class = PublisherListSerializer
    permission_classes = [AllowAny]
    queryset = Publisher.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)


class PublisherDetailsAPIView(RetrieveAPIView):
    serializer_class = PublisherDetailsSerializer
    queryset = Publisher.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'publisher_id'
    lookup_field = 'id'


class WriterTranslatorListAPIView(ListAPIView):
    serializer_class = WriterTranslatorListSerializer
    permission_classes = [AllowAny]
    queryset = WriterTranslator.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)


class WriterTranslatorDetailAPIView(RetrieveAPIView):
    serializer_class = WriterTranslatorDetailsSerializer
    queryset = WriterTranslator.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'library_id'
    lookup_field = 'id'
