# -*- coding: utf-8 -*-


from django.db.models import Count, Q, F
from django.utils.translation import ugettext as _
from rest_framework import filters
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.serializers import as_serializer_error
from rest_framework.validators import ValidationError

from aparnik.contrib.basemodels.api.views import BaseModelSortAPIView
from aparnik.contrib.suit.api.views import BaseListAPIView
from .serializers import QAListSerializer, QADetailSerializer, QACreateSerializer
from ..models import QA
from aparnik.contrib.reviews.api.serializers import BaseReviewListPolymorphicSerializer, BaseReviewDetailsPolymorphicSerializer


class QASortAPIView(BaseModelSortAPIView):
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super(BaseModelSortAPIView, self).__init__(*args, **kwargs)
        command_dict = {
            'visit_count': {
                'label': 'تعداد نمایش',
                'queryset_filter': Q(),
                'annotate_command': {},
                'key_sort': 'visit_count',
            },
            'review_count': {
                'label': 'تعداد نظرات',
                'queryset_filter': Q(),
                'annotate_command': {'sort_key': Count('reviews_set')},
                'key_sort': 'sort_key',
            },
            'like_count': {
                'label': 'محبوب ترین ها',
                'queryset_filter': Q(),
                'annotate_command': {'sort_key': Count('like')},
                'key_sort': 'sort_key',
            }
        }
        self.command_dict.update(command_dict)


class QAListAPIView(BaseListAPIView):
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
            if 'mine' in self.request.query_params and user.is_authenticated:
                queryset = queryset.filter(user_obj=user)
            # queryset
        elif user.is_authenticated:
            queryset = QA.objects.get_this_user(user=user)

        return queryset

    def get_sort_api(self, request):
        return QASortAPIView(request=request)



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
