from django.utils import timezone
from rest_framework.decorators import action
from .base import TokenAuthedViewSet
from issuestracker.models import Category
from issuestracker.serializers import (
    CategorySerializer,
    CategoryListSerializer,
)


class CategoryViewset(TokenAuthedViewSet):
    queryset = Category.objects.all()
    lookup_field = "slug"
    pagination_class = None
    throttle_classes = []

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return CategoryListSerializer
        return CategorySerializer

    @action(detail=True, methods=["post"])
    def publish(self, request, *args, **kwargs):
        slug = request.data.get("slug")

        update = self.update(request, *args, **kwargs)

        print("Publish too!")

        c = Category.objects.get(slug=slug)
        c.last_published = timezone.now()
        c.save()

        return update
