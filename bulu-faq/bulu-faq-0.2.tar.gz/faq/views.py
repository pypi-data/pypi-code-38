from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

from .models import Category, FAQ
from .serializers import CategorySerializer, FAQSerializer


class BaseViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    renderer_classes = [JSONRenderer]
    pagination_class = None


class FAQViewSet(BaseViewSet):
    queryset = FAQ.objects.order_by('order')
    serializer_class = FAQSerializer


class FAQCategoryViewSet(BaseViewSet):
    queryset = Category.objects.order_by('order', 'name')
    serializer_class = CategorySerializer
