# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from rest_framework.decorators import list_route, detail_route
from .apps import Config
from rest_framework.response import Response

__author__ = 'denishuang'
from . import models, serializers, permissions
from rest_framework import viewsets, mixins, status
from django_szuprefix.api.helper import register
from ..saas.mixins import PartyMixin
from django_szuprefix.api.mixins import UserApiMixin


class ManufacturerViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Manufacturer.objects.all()
    serializer_class = serializers.ManufacturerSerializer
    search_fields = ('name', 'code')
    filter_fields = {
        'name': ['exact', 'in'],
    }


register(Config.label, 'manufacturer', ManufacturerViewSet)


class CompanyViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    search_fields = ('name', 'code')
    filter_fields = {
        'name': ['exact', 'in'],
        'is_customer': ['exact'],
        'is_vendor': ['exact']
    }


register(Config.label, 'company', CompanyViewSet)


class ProductViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    search_fields = ('name', 'code', 'number', 'manufacturer__name', 'manufacturer__code')
    filter_fields = {
        'name': ['exact', 'in'],
        'number': ['exact', 'in'],
        'manufacturer': ['exact', 'in']
    }


register(Config.label, 'product', ProductViewSet)


class QuoteViewSet(UserApiMixin, PartyMixin, mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer
    search_fields = ("product__name", "product__code", "vendor__name", "vendor__code")
    filter_fields = ("product",)


register(Config.label, 'quote', QuoteViewSet)


class RequestViewSet(UserApiMixin, PartyMixin, viewsets.ModelViewSet):
    queryset = models.Request.objects.all()
    serializer_class = serializers.RequestSerializer
    search_fields = ("customer__name",)
    filter_fields = {
        'status': ['exact', 'in'],
        'customer': ['exact', 'in'],
        'create_time': ['gt', 'lt']
    }

    @detail_route(["get"])
    def items(self, request, pk=None):
        q_request = self.get_object()
        page = self.paginate_queryset(q_request.items.all())
        serializer = serializers.ItemSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @detail_route(["put"])
    def change_status(self, request, pk=None):
        q_request = self.get_object()
        serializer = serializers.RequestChangeStatusSerializer(q_request, data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            serializer = serializers.RequestSerializer(instance)
            return Response(serializer.data)


register(Config.label, 'request', RequestViewSet)


class ItemViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    filter_fields = {"product": ['exact'], "request": ['exact'], "id": ["lt"]}
    permission_classes = [permissions.CanDeleteRequestItem]

    @detail_route(["get"])
    def quotes(self, request, pk=None):
        item = self.get_object()
        page = self.paginate_queryset(item.quotes.all())
        serializer = serializers.QuoteSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


register(Config.label, 'item', ItemViewSet)
