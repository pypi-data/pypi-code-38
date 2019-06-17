# -*- coding: utf-8 -*-


from django.db.models import Count
from django.utils.translation import ugettext as _
from rest_framework import filters
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.serializers import as_serializer_error
from rest_framework.validators import ValidationError

from .serializers import QAListSerializer, QADetailSerializer, QACreateSerializer
from ..models import QA
from aparnik.contrib.reviews.api.serializers import BaseReviewListPolymorphicSerializer, BaseReviewDetailsPolymorphicSerializer


qa_sort_content = [
    {
        'key': 'visit_count',
        'label': 'نمایش'
    },{
        'key': 'review_count',
        'label': 'تعداد نظرات'
    },{
        'key': 'like_count',
        'label': 'محبوب ترین ها'
    }
]


class QASortAPIView(APIView):
    permission_classes = [AllowAny]

    """
        A view that returns the count of active users in JSON.
        """

    def get(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}
        try:
            content = qa_sort_content
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))


class QAListAPIView(ListAPIView):
    serializer_class = BaseReviewListPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = [filters.OrderingFilter, ]
    # ordering_fields = ['visit_count', 'like_count', 'dislike_count', ]
    # ordering = ['visit_count', ]
    search_fields = ('title',)

    def get_queryset(self):
        user = self.request.user
        queryset = QA.objects.all()
        if 'model_id' in self.request.parser_context['kwargs']:
            dict = {
                'model_obj': self.request.parser_context['kwargs']['model_id'],
                'user_obj': None
            }
            if user.is_authenticated:
                dict['user_obj'] = user
            queryset = QA.objects.model_question_answer(**dict)
            # queryset
        if user.is_authenticated:
            queryset = QA.objects.get_this_user(user=user)

        # find order
        allow_ordering = [x['key'] for x in qa_sort_content]
        if 'ordering' in self.request.query_params:
            ordering = self.request.query_params['ordering']
            ordering_field = ordering.lstrip('-')
            if ordering_field in allow_ordering:
                if ordering_field == 'like_count':
                    # TODO: move like count and etc to management base reviews
                    queryset = queryset.annotate(like_count=Count('like'))
                elif ordering_field == 'review_count':
                    queryset = queryset.annotate(review_count=Count('review_obj'))
                queryset = queryset.order_by(ordering)
        return queryset


class QADetailAPIView(RetrieveAPIView):
    serializer_class = BaseReviewDetailsPolymorphicSerializer
    queryset = QA.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'qa_id'
    lookup_field = 'id'


class QACreateAPIView(CreateAPIView):
    serializer_class = QACreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        files = self.request.POST.get('files', None)
        if files:
            files = files.split(',')
        dict = {
            'user_obj': user,
            'files': []
        }

        if files:
            dict['files'] = files
        serializer.save(**dict)
