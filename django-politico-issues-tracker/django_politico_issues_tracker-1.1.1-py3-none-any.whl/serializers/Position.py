from rest_framework import serializers
from issuestracker.models import Position, Candidate

from .Candidate import CandidateSerializer


class PositionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)

    def update_candidates(self, instance, candidates):
        candidate_ids = [c["id"] for c in candidates]
        # Remove candidates that were removed
        for c in instance.candidates.all():
            if c.id not in candidate_ids:
                instance.candidates.remove(c)

        # Add candidates that were added
        for c in candidates:
            try:
                instance.candidates.get(id=c["id"])
            except Candidate.DoesNotExist:
                instance.candidates.add(Candidate.objects.get(id=c["id"]))

    def create(self, validated_data):
        candidates = validated_data.pop("candidates", [])
        p = Position(**validated_data)
        p.save()
        self.update_candidates(p, candidates)
        return p

    def update(self, instance, validated_data):
        candidates = validated_data.get("candidates", [])
        self.update_candidates(instance, candidates)

        instance.name = validated_data.get("name", instance.name)
        instance.explanation = validated_data.get(
            "explanation", instance.explanation
        )
        instance.issue = validated_data.get("issue", instance.issue)
        instance.order = validated_data.get("order", instance.order)
        instance.save()
        return instance

    class Meta:
        model = Position
        fields = "__all__"


class PositionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ("name", "explanation")
