from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import (AllowAny, IsAuthenticated)

from ..models import Slider
from .serializers import SliderDetailsPolymorphicSerializer  # , Serializer, UserCreateSerializer


class SliderListAPIView(ListAPIView):
    serializer_class = SliderDetailsPolymorphicSerializer
    permission_classes = [AllowAny]
    queryset = Slider.objects.all()
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'image')


class SliderDetailAPIView(RetrieveAPIView):
    serializer_class = SliderDetailsPolymorphicSerializer
    queryset = Slider.objects.all()
    permission_classes = [AllowAny]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'
