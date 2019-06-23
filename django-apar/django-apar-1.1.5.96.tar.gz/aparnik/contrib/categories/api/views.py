from django.db.models import Q
from django.utils.translation import ugettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework import filters

from django.shortcuts import get_object_or_404
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from aparnik.contrib.basemodels.models import BaseModel
from ..models import Category#, CategoryCourse, CategoryLibrary
from .serializers import CategoryListPolymorphicSerializer, CategoryDetailsPolymorphicSerializer


class CategoryListAPIView(ListAPIView):
    serializer_class = CategoryListPolymorphicSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_fields = ('description', 'title',)
    search_fields = ('description', 'title',)

    def get_queryset(self):
        queryset = Category.objects.all()

        if 'category_id' in self.kwargs:
            queryset = Category.objects.childs(category_obj=self.kwargs['category_id'])

        return queryset


class CategoryListModelAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        queryset = []
        if 'category_id' in self.kwargs:
            category = get_object_or_404(Category, id=self.kwargs['category_id'])
            queryset = BaseModel.objects.active().filter(Q(Book___category_obj=category) |
                                                         Q(Course___category_obj=category))
        return queryset


class CategoryDetailAPIView(RetrieveAPIView):
    serializer_class = CategoryDetailsPolymorphicSerializer
    queryset = Category.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'category_id'
    lookup_field = 'id'
