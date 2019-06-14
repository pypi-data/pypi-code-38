from issuestracker.models import Candidate
from rest_framework import serializers


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = "__all__"
