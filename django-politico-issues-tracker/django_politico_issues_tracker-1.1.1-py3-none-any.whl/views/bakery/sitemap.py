from .base import BakeryBase
from rest_framework.response import Response
from issuestracker.models import Category, Issue, Candidate
from issuestracker.serializers.bakery.SiteMap import (
    CategorySerializer,
    IssueSerializer,
    CandidateSerializer,
)


class BakerySitemap(BakeryBase):
    def get(self, request, format=None):
        return Response(
            {
                "category": [
                    d["slug"]
                    for d in CategorySerializer(
                        Category.live.all(), many=True
                    ).data
                ],
                "issue": [
                    d["slug"]
                    for d in IssueSerializer(Issue.live.all(), many=True).data
                ],
                "candidate": [
                    d["slug"]
                    for d in CandidateSerializer(
                        Candidate.objects.all(), many=True
                    ).data
                ],
            }
        )
