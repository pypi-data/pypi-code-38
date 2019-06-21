from issuestracker.models import Story
from rest_framework import serializers


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"
