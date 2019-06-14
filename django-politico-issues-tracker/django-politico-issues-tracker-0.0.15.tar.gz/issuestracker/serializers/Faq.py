from issuestracker.models import Faq
from rest_framework import serializers


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"
