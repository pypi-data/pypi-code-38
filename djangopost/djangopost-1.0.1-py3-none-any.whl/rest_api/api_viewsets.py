from rest_framework import generics
from django.db.models import Q
from rest_framework import filters
from ..models import CategoryModel
from .api_serializers import CategorySerializer
from .api_permissions import IsOwnerOrReadOnly


class CategoryListViewset(generics.ListAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'description')
    ordering_fields = ('author',)


class CategoryRetrieveViewset(generics.RetrieveAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class CategoryUpdateViewset(generics.RetrieveUpdateAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class CategoryDestroyViewset(generics.DestroyAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]


class CategoryCreateViewset(generics.CreateAPIView):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
      