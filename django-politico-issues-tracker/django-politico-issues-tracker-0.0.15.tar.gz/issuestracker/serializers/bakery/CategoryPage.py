from rest_framework import serializers
from issuestracker.models import Category, Issue, Candidate, Story
from django.db.models import Q


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ("headline", "link")


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ("uid",)


class IssueSerializer(serializers.ModelSerializer):
    position_count = serializers.SerializerMethodField()
    candidates_with_position_count = serializers.SerializerMethodField()

    def get_position_count(self, obj):
        return obj.position_set.all().count()

    def get_candidates_with_position_count(self, obj):
        count = 0
        for position in obj.position_set.all():
            count += position.candidates.count()

        return count

    class Meta:
        model = Issue
        fields = (
            "name",
            "slug",
            "dek",
            "position_count",
            "candidates_with_position_count",
        )


class CategorySerializer(serializers.ModelSerializer):
    issue_set = IssueSerializer(many=True, read_only=True)
    candidates_count = serializers.SerializerMethodField()
    story_set = serializers.SerializerMethodField()

    def get_candidates_count(self, obj):
        return Candidate.objects.all().count()

    def get_story_set(self, obj):
        stories = Story.objects.filter(Q(issue__category=obj))
        return StorySerializer(stories, many=True).data

    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
            "icon",
            "social_image",
            "summary",
            "seo_name",
            "candidates_count",
            "issue_set",
            "story_set",
        )
