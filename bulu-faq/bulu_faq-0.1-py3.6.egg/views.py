from rest_framework import mixins
from rest_framework import viewsets

from .models import Category, FAQ
from .serializers import CategorySerializer, FAQSerializer


class BaseViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    pass


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class FAQViewSet(BaseViewSet):
    queryset = FAQ.objects.order_by('category', 'order')
    serializer_class = FAQSerializer
