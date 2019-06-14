from rest_framework import serializers
from issuestracker.models import Category, Issue, Candidate, Position, Story


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ("headline", "link")


class CandidateSerializer(serializers.ModelSerializer):
    view_count = serializers.SerializerMethodField()

    def get_view_count(self, obj):
        return Position.objects.filter(candidates=obj).count()

    class Meta:
        model = Candidate
        fields = ("uid", "view_count")


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("name", "slug")


class CategorySerializer(serializers.ModelSerializer):
    issue_set = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("name", "slug", "icon", "issue_set")
