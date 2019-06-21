from .base import BakeryBase
from rest_framework.response import Response
from issuestracker.models import Issue, Candidate, Story, Category
from issuestracker.serializers.bakery.SiteMap import CombinedSerializer
from issuestracker.serializers.bakery.IssuePage import (
    IssueSerializer,
    CandidateSerializer,
    StorySerializer,
)


class BakeryIssue(BakeryBase):
    def get(self, request, issue=None):
        selected_issue = Issue.live.get(slug=self.kwargs["issue"])
        last_updated = selected_issue.last_published

        if last_updated is not None:
            last_updated = last_updated.isoformat(" ")

        return Response(
            {
                "last_updated": last_updated,
                "data": IssueSerializer(selected_issue).data,
                "candidates": CandidateSerializer(
                    Candidate.objects.all(), many=True
                ).data,
                "latest_coverage": StorySerializer(
                    Story.objects.order_by("-date_added"), many=True
                ).data[0:3],
                "sitemap": CombinedSerializer(
                    Category.live.all(), many=True
                ).data,
            }
        )
