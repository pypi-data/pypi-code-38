from issuestracker.models import Issue
from rest_framework import serializers
from .Position import PositionSerializer
from .Faq import FaqSerializer
from .Story import StorySerializer


class IssueSerializer(serializers.ModelSerializer):
    position_set = PositionSerializer(many=True, read_only=True)
    faq_set = FaqSerializer(many=True, read_only=True)
    story_set = StorySerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = (
            "id",
            "name",
            "slug",
            "dek",
            "summary",
            "category",
            "position_set",
            "faq_set",
            "story_set",
            "status",
            "last_updated",
            "last_published",
        )


class IssueListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("name", "slug", "dek", "category")
