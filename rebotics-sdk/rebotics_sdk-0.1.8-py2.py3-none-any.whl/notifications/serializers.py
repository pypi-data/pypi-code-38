from rest_framework import serializers

from rebotics_sdk.notifications.models import WebhookRouter


class SetWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookRouter
        fields = [
            'url',
            'auth_token'
        ]
        extra_kwargs = {
            'auth_token': {'required': False},
        }
