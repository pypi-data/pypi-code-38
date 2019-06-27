from django.utils.translation import ugettext as _
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from django.shortcuts import get_object_or_404

from ..models import Page
from .serializers import PageListPolymorphicSerializer


class PageListAPIView(ListAPIView):
    serializer_class = PageListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        queryset = Page.objects.active()
        return queryset
