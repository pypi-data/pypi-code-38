# -*- coding: utf-8 -*-


from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from ..models import BaseSegment
from .serializers import BaseSegmentListPolymorphicSerializer
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer


class BaseSegmentListAPIView(ListAPIView):
    serializer_class = BaseSegmentListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        queryset = BaseSegment.objects.all()
        if 'segment_id' in self.request.parser_context['kwargs']:
            queryset = BaseSegment.objects.filter(id=self.request.parser_context['kwargs']['segment_id'])
        return queryset


class BaseSegmentModelListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [AllowAny]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        if 'segment_id' in self.request.parser_context['kwargs']:
            segment = BaseSegment.objects.filter(id=self.request.parser_context['kwargs']['segment_id']).first()
            queryset = segment.model_obj.all()
        return queryset
