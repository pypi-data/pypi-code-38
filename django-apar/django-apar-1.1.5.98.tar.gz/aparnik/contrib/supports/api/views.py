from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import (AllowAny, IsAuthenticated)

from ..models import Support
from .serializers import SupportDetailsSerializer  # , Serializer, UserCreateSerializer


class SupportListAPIView(ListAPIView):
    serializer_class = SupportDetailsSerializer
    permission_classes = [AllowAny]
    queryset = Support.objects.active()
    # filter_backends = (filters.SearchFilter,)search_fields = ('title')


class SupportDetailAPIView(RetrieveAPIView):
    serializer_class = SupportDetailsSerializer
    queryset = Support.objects.active()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
