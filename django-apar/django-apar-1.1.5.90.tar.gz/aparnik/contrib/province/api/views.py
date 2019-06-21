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

from aparnik.contrib.province.models import Province, City, Shahrak, Town
from aparnik.contrib.province.api.serializers import ProvinceListSerializer, ProvinceCreateSerializer, ProvinceDetailSerializer, \
    CityListSerializer, CityCreateSerializer, CityDetailSerializer, \
    ShahrakCreateSerializer, ShahrakDetailSerializer, ShahrakListSerializer, \
    TownCreateSerializer, TownDetailSerializer, TownListSerializer

permission_create = [IsAdminUser]
permission_read = [AllowAny]

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10

def get_province(kwargs):
    return kwargs.get('province_id', 0)

def get_city(kwargs):
    return kwargs.get('city_id', 0)

class ProvinceListAPIView(ListAPIView):
    serializer_class = ProvinceListSerializer
    permission_classes = permission_read
    # http_method_names = ['get']
    queryset = Province.objects.all()
    pagination_class = LargeResultsSetPagination

class ProvinceCreateAPIView(CreateAPIView):
    serializer_class = ProvinceCreateSerializer
    permission_classes = permission_create
    #http_method_names = ['get']

class ProvinceDetailAPIView(RetrieveAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceDetailSerializer
    permission_classes = permission_read
    lookup_field = 'id'

# City
class CityListAPIView(ListAPIView):
    serializer_class = CityListSerializer
    permission_classes = permission_read
    # http_method_names = ['get']
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        province = get_province(self.kwargs)
        return City.objects.filter(province=province)

class CityCreateAPIView(CreateAPIView):
    serializer_class = CityCreateSerializer
    permission_classes = permission_create
    #http_method_names = ['get']

class CityDetailAPIView(RetrieveAPIView):
    queryset = City.objects.all()
    serializer_class = CityDetailSerializer
    permission_classes = permission_read
    lookup_field = 'id'

# Shahrak
class ShahrakListAPIView(ListAPIView):
    serializer_class = ShahrakListSerializer
    permission_classes = permission_read
    # http_method_names = ['get']
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        province = get_province(self.kwargs)
        return Shahrak.objects.filter(province=province)

class ShahrakCreateAPIView(CreateAPIView):
    serializer_class = ShahrakCreateSerializer
    permission_classes = permission_create
    #http_method_names = ['get']

class ShahrakDetailAPIView(RetrieveAPIView):
    queryset = Shahrak.objects.all()
    serializer_class = ShahrakDetailSerializer
    permission_classes = permission_read
    lookup_field = 'id'

# Town
class TownListAPIView(ListAPIView):
    serializer_class = TownListSerializer
    permission_classes = permission_read
    # http_method_names = ['get']
    queryset = Town.objects.all()
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):

        city = get_city(self.kwargs)
        return Town.objects.filter(city=city)

class TownCreateAPIView(CreateAPIView):
    serializer_class = TownCreateSerializer
    permission_classes = permission_create
    #http_method_names = ['get']

class TownDetailAPIView(RetrieveAPIView):
    queryset = Town.objects.all()
    serializer_class = TownDetailSerializer
    permission_classes = permission_read
    lookup_field = 'id'