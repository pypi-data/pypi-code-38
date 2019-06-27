# -*- coding: utf-8 -*-


from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BookmarkListSerializer, BookmarkDetailSerializer
from aparnik.contrib.bookmarks.models import Bookmark
from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from aparnik.contrib.basemodels.models import BaseModel


class BookmarkListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return BaseModel.objects.filter(id__in=Bookmark.objects.get_this_user(user=user).values_list('model_obj__id', flat=True))


class BookmarkDetailAPIView(RetrieveAPIView):
    serializer_class = BookmarkDetailSerializer
    queryset = Bookmark.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'bookmark_id'
    lookup_field = 'id'


class BookmarkSetAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, model_id, format=None, *args, **kwargs):
        status = HTTP_400_BAD_REQUEST
        user = self.request.user

        content = {
            'is_bookmark': False,
        }

        model = get_object_or_404(BaseModel.objects.all(), id=model_id)

        try:
            bookmark = get_object_or_404(Bookmark.objects.models(model=model_id), user_obj=user)
            bookmark.delete()
            status = HTTP_200_OK

        except Exception as e:
            try:
                bookmark = Bookmark.objects.create(user_obj=user, model_obj=model)
                bookmark.save()
                content['is_bookmark'] = True
                status = HTTP_200_OK
            except Exception as e:
                pass

        return Response(content, status=status)
