from issuestracker.models import Category
from rest_framework import serializers
from .Issue import IssueListSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
            "icon",
            "summary",
            "status",
            "last_updated",
            "last_published",
        )


class CategoryListSerializer(serializers.ModelSerializer):
    issue_set = IssueListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "summary", "slug", "icon", "issue_set")
