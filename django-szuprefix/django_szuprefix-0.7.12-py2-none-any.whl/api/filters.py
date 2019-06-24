# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django_filters.rest_framework import filters

class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)