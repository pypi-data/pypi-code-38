from rest_framework import serializers


class WebhookDataSerializer(serializers.Serializer):
    status = serializers.CharField()
    component = serializers.CharField()
    body = serializers.JSONField()
