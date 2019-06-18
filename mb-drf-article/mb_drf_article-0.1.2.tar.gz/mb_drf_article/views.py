"""Article views."""

from rest_framework import generics

from .serializers import ArticleSerializer
from .permissions import IsAdminUserOrReadOnly
from .models import Article


class ArticleList(generics.ListCreateAPIView):
    """Article list view."""

    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    """Article detail view."""

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    lookup_field = ('slug_title')
