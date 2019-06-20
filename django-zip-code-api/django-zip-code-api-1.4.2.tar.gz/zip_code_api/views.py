# -*- coding: utf-8 -*-
from congo.utils.classes import get_class
from rest_framework import permissions, generics
from rest_framework.decorators import api_view
from zip_code_api.conf import settings
from zip_code_api.models import Address
from zip_code_api.serializers import AddressListSerializer

class AddressList(generics.ListAPIView):
    model = Address
    queryset = Address.objects.all()
    serializer_class = AddressListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@api_view()
def zip_code(request):
    country = request.GET.get('country')
    zip_code = request.GET.get('zip_code')

    queryset = Address.objects.filter(country = country).values_list('zip_code', flat = True).distinct()

    if zip_code:
        queryset = queryset.filter(zip_code__startswith = zip_code)
    else:
        queryset = queryset.none()

    pagination_class = get_class(settings.ZIP_CODE_PAGINATION_CLASS)
    paginator = pagination_class()
    result = paginator.paginate_queryset(queryset, request)

    return paginator.get_paginated_response([{'zip_code': obj} for obj in result])

@api_view()
def city(request):
    country = request.GET.get('country')
    zip_code = request.GET.get('zip_code')
    city = request.GET.get('city')

    queryset = Address.objects.filter(country = country, city__isnull = False).values_list('city', flat = True).distinct()

    if zip_code:
        queryset = queryset.filter(zip_code__startswith = zip_code)
    if city:
        queryset = queryset.filter(city__istartswith = city)
    if not (zip_code or city):
        queryset = queryset.none()

    pagination_class = get_class(settings.ZIP_CODE_PAGINATION_CLASS)
    paginator = pagination_class()
    result = paginator.paginate_queryset(queryset, request)

    return paginator.get_paginated_response([{'city': obj} for obj in result])

@api_view()
def street(request):
    country = request.GET.get('country')
    zip_code = request.GET.get('zip_code')
    city = request.GET.get('city')
    street = request.GET.get('street')

    queryset = Address.objects.filter(country = country, street__isnull = False).values_list('street', flat = True).distinct()

    if zip_code:
        queryset = queryset.filter(zip_code__startswith = zip_code)
    if city:
        queryset = queryset.filter(city__startswith = city)
    if street:
        queryset = queryset.filter(street__icontains = street)
    if not (zip_code or city or street):
        queryset = queryset.none()

    pagination_class = get_class(settings.ZIP_CODE_PAGINATION_CLASS)
    paginator = pagination_class()
    result = paginator.paginate_queryset(queryset, request)

    return paginator.get_paginated_response([{'street': obj} for obj in result])

@api_view()
def address(request):
    country = request.GET.get('country')
    zip_code = request.GET.get('zip_code')
    city = request.GET.get('city')
    street = request.GET.get('street')

    queryset = Address.objects.filter(country = country)

    if zip_code:
        queryset = queryset.filter(zip_code__startswith = zip_code)
    if city:
        queryset = queryset.filter(city__startswith = city)
    if street:
        queryset = queryset.filter(street__icontains = street)
    if not (zip_code or city or street):
        queryset = queryset.none()

    pagination_class = get_class(settings.ZIP_CODE_PAGINATION_CLASS)
    paginator = pagination_class()
    result = paginator.paginate_queryset(queryset, request)

    return paginator.get_paginated_response([{'country': obj.country, 'zip_code': obj.zip_code, 'city': obj.city, 'street': obj.street} for obj in result])
