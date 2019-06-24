from rest_framework import serializers
from issuestracker.models import Category, Issue


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("slug",)


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("slug", "name")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("slug", "name")


class CombinedSerializer(serializers.ModelSerializer):
    issue_set = serializers.SerializerMethodField()

    def get_issue_set(self, obj):
        return IssueSerializer(
            obj.issue_set.filter(status="live"), many=True, read_only=True
        ).data

    class Meta:
        model = Category
        fields = ("slug", "name", "icon", "issue_set")
