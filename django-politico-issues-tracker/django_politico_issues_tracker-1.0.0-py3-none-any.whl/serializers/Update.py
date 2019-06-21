from issuestracker.models import Update
from rest_framework import serializers


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = ("text", "issue", "created_on")
