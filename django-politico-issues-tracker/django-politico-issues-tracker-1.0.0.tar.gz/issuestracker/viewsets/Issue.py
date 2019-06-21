import logging
from .base import TokenAuthedViewSet
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from issuestracker.utils.update_fk_models import update_fk_models
from issuestracker.models import Issue, Position, Faq, Story
from issuestracker.serializers import (
    IssueSerializer,
    IssueListSerializer,
    PositionSerializer,
    FaqSerializer,
    StorySerializer,
)

logger = logging.getLogger("serializer")
tasks_logger = logging.getLogger("tasks")


class IssueViewset(TokenAuthedViewSet):
    queryset = Issue.objects.all()
    lookup_field = "slug"
    pagination_class = None
    throttle_classes = []

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return IssueListSerializer
        return IssueSerializer

    def update(self, request, *args, **kwargs):
        id = request.data.pop("id")
        story_data = request.data.pop("story_set")
        faq_data = request.data.pop("faq_set")
        position_data = request.data.pop("position_set")
        instance = Issue.objects.get(pk=id)

        update_fk_models(instance, story_data, Story, StorySerializer)
        update_fk_models(instance, faq_data, Faq, FaqSerializer)
        update_fk_models(
            instance,
            position_data,
            Position,
            PositionSerializer,
            context_keys=["candidates"],
        )

        s = IssueSerializer(instance, data=request.data)

        if not s.is_valid():
            logger.error(s.errors)

        s.is_valid(raise_exception=True)

        s.save()

        return Response(s.data)

    def partial_update(self, request, *args, **kwargs):
        return Response(
            "Partial updates are not allowed at this endpoint.",
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, *args, **kwargs):
        slug = request.data.get("slug")

        update = self.update(request, *args, **kwargs)

        tasks_logger.info("Publish Too!")

        i = Issue.objects.get(slug=slug)
        i.last_published = timezone.now()
        i.save()

        return update
