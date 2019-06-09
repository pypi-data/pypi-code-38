# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.serializers import as_serializer_error
from rest_framework.exceptions import ValidationError


from .serializers import BaseReviewListPolymorphicSerializer, BaseReviewDetailsPolymorphicSerializer, \
    LikeListSerializer, LikeDetailsSerializer, ReviewCreateSerializer
from ..models import Review, Like, BaseReview


class BaseReviewStatusSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'is_published': False,
        }

        try:
            obj = get_object_or_404(BaseReview.objects.all(), id=review_id)
            obj.is_published = not obj.is_published
            obj.save()
            content['is_published'] = obj.is_published
            status = HTTP_200_OK

        except Exception as e:
            raise ValidationError(as_serializer_error(e))

        return Response(content, status=status)


class ReviewListAPIView(ListAPIView):
    serializer_class = BaseReviewListPolymorphicSerializer
    permission_classes = [AllowAny]
    # queryset = Review.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        user = self.request.user
        queryset = Review.objects.all().filter(parent_obj__isnull=True)

        if 'model_id' in self.request.parser_context['kwargs']:
            # Review for model
            dict = {
                'model_obj': self.request.parser_context['kwargs']['model_id'],
                'user_obj': None
            }
            if user.is_authenticated():
                dict['user_obj'] = user
            queryset = Review.objects.model_reviews(**dict)
            return queryset

        if user.is_authenticated():
            # Mine Review
            return Review.objects.get_this_user(user=user).filter(parent_obj__isnull=True)

        return queryset


class ReviewDetailAPIView(RetrieveAPIView):
    serializer_class = BaseReviewDetailsPolymorphicSerializer
    permission_classes = [AllowAny]
    queryset = Review.objects.all()
    lookup_url_kwarg = 'review_id'
    lookup_field = 'id'


class ReviewCreateAPIView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user_obj=user)


class LikeListAPIView(ListAPIView):
    serializer_class = LikeListSerializer
    permission_classes = [AllowAny]
    # queryset = Like.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        queryset = Like.objects.all()
        if 'review_id' in self.request.parser_context['kwargs']:
            queryset = Like.objects.like(review_obj=self.request.parser_context['kwargs']['review_id'])
        return queryset


class LikeDetailAPIView(RetrieveAPIView):
    serializer_class = LikeDetailsSerializer
    queryset = Like.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'like_id'
    lookup_field = 'id'


class DislikeListAPIView(ListAPIView):
    serializer_class = LikeListSerializer
    permission_classes = [AllowAny]
    # queryset = Like.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('id',)

    def get_queryset(self):
        queryset = Like.objects.all()
        if 'review_id' in self.request.parser_context['kwargs']:
            queryset = Like.objects.dislike(review_obj=self.request.parser_context['kwargs']['review_id'])
        return queryset


class LikeReviewSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'is_like': False,
        }

        review = get_object_or_404(BaseReview.objects.all(), id=review_id)

        try:

            like = get_object_or_404(Like.objects.review(review_obj=review), user_obj=user)

            if not like.is_like:
                like.is_like = True
                like.save()
                content['is_like'] = True
                status = HTTP_200_OK
                return Response(content, status=status)

            if like.is_like:
                like.delete()

            status = HTTP_200_OK

        except Exception as e:
            try:
                like = Like.objects.create(user_obj=user, review_obj=review, is_like=True)
                like.save()
                content['is_like'] = True
                status = HTTP_200_OK
            except Exception as e:
                pass

        return Response(content, status=status)


class DislikeReviewSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'is_dislike': False,
        }

        review = get_object_or_404(BaseReview.objects.all(), id=review_id)

        try:

            like = get_object_or_404(Like.objects.review(review_obj=review), user_obj=user)

            if like.is_like:
                like.is_like = False
                content['is_dislike'] = True
                like.save()
                status = HTTP_200_OK
                return Response(content, status=status)

            like.delete()
            status = HTTP_200_OK

        except Exception as e:
            try:
                like = Like.objects.create(user_obj=user, review_obj=review, is_like=False)
                like.save()
                content['is_dislike'] = True
                status = HTTP_200_OK
            except Exception as e:
                pass

        return Response(content, status=status)
