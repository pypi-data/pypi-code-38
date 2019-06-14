from rest_framework import serializers
from issuestracker.models import Category, Issue, Candidate, Position, Story


def get_position(obj, slug):
    candidate_slug = slug
    c = Candidate.objects.get(slug=candidate_slug)
    return c.position_set.get(issue=obj.id)


def get_candidates_with_position_count(obj):
    count = 0
    for position in obj.position_set.all():
        count += position.candidates.count()

    return count


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ("headline", "link")


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ("uid",)


class IssueSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    explanation = serializers.SerializerMethodField()
    like_candidates = serializers.SerializerMethodField()

    def get_position(self, obj):
        try:
            return get_position(obj, self.context["slug"]).name
        except Position.DoesNotExist:
            return None

    def get_explanation(self, obj):
        try:
            return get_position(obj, self.context["slug"]).explanation
        except Position.DoesNotExist:
            return None

    def get_like_candidates(self, obj):
        candidate_slug = self.context["slug"]
        try:
            position = get_position(obj, self.context["slug"])
            return [
                cand.uid
                for cand in position.candidates.all()
                if cand.slug != candidate_slug
            ]
        except Position.DoesNotExist:
            return []

    class Meta:
        model = Issue
        fields = ("name", "slug", "position", "explanation", "like_candidates")


class CategorySerializer(serializers.ModelSerializer):
    issue_set = serializers.SerializerMethodField()

    def get_issue_set(self, obj):
        return IssueSerializer(
            self.context["issues"].filter(category=obj),
            many=True,
            read_only=True,
            context=self.context,
        ).data

    class Meta:
        model = Category
        fields = ("name", "slug", "icon", "issue_set")
