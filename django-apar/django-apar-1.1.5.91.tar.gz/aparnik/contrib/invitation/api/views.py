# -*- coding: utf-8 -*-


from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.generics import (
    CreateAPIView,
    # DestroyAPIView,
    ListAPIView,
    # UpdateAPIView,
    RetrieveAPIView,
    # RetrieveUpdateAPIView
    )
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

    )
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from aparnik.contrib.invitation.models import Invite
from aparnik.contrib.invitation.api.serializers import InviteListSerializer, InviteDetailSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10


class InviteListAPIView(ListAPIView):
    serializer_class = InviteListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        return Invite.objects.filter(invited_by=user)


class InviteDetailAPIView(RetrieveAPIView):
    queryset = Invite.objects.all()
    serializer_class = InviteDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user

        return Invite.objects.filter(invited_by=user)
