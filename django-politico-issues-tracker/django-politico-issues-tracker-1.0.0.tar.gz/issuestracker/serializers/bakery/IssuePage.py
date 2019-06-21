from rest_framework import serializers
from django.db.models import Q
from issuestracker.models import Faq, Story, Position, Issue, Candidate, Story


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ("headline", "link")


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ("uid",)


class PositionSerializer(serializers.ModelSerializer):
    candidates = serializers.SerializerMethodField()

    def get_candidates(self, obj):
        return [candidate.uid for candidate in obj.candidates.all()]

    class Meta:
        model = Position
        fields = ("name", "explanation", "candidates")


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ("question", "answer")


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ("headline", "link")


class IssueSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()
    category_icon = serializers.SerializerMethodField()
    faq_set = FaqSerializer(many=True, read_only=True)
    story_set = StorySerializer(many=True, read_only=True)
    position_set = PositionSerializer(many=True, read_only=True)
    candidates_count = serializers.SerializerMethodField()
    candidates_with_position_count = serializers.SerializerMethodField()
    candidates_with_no_position = serializers.SerializerMethodField()

    def get_category(self, obj):
        return str(obj.category)

    def get_category_slug(self, obj):
        return obj.category.slug

    def get_category_icon(self, obj):
        return obj.category.icon

    def get_candidates_with_position_count(self, obj):
        count = 0
        for position in obj.position_set.all():
            count += position.candidates.count()

        return count

    def get_candidates_count(self, obj):
        return Candidate.objects.all().count()

    def get_candidates_with_no_position(self, obj):
        queryset = Candidate.objects.filter(~Q(position__issue=obj))
        return CandidateSerializer(queryset, many=True).data

    class Meta:
        model = Issue
        fields = (
            "name",
            "slug",
            "seo_name",
            "social_image",
            "category",
            "category_slug",
            "category_icon",
            "summary",
            "faq_set",
            "story_set",
            "position_set",
            "candidates_count",
            "candidates_with_position_count",
            "candidates_with_no_position",
        )
