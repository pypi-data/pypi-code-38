from .base import BakeryBase
from django.db.models import Q
from rest_framework.response import Response
from issuestracker.models import Category, Candidate, Story, Issue
from issuestracker.serializers.bakery.SiteMap import CombinedSerializer
from issuestracker.serializers.bakery.CandidatePage import (
    CategorySerializer,
    CandidateSerializer,
    StorySerializer,
)


class BakeryCandidate(BakeryBase):
    def get(self, request, candidate=None):
        selected_cand_query = Candidate.objects.filter(
            slug=self.kwargs["candidate"]
        )
        selected_cand = selected_cand_query.first()

        issues = Issue.live.filter(
            Q(position__candidates__in=selected_cand_query)
        )
        categories = Category.live.filter(Q(issue__in=issues)).distinct()

        category_data = CategorySerializer(
            categories,
            context={"slug": candidate, "issues": issues},
            many=True,
        ).data

        last_updated_issue = issues.order_by("-last_published").first()

        last_updated_category = categories.order_by("-last_published").first()

        last_updated = self.get_last_updated(
            last_updated_category, last_updated_issue
        )

        return Response(
            {
                "uid": selected_cand.uid,
                "last_updated": last_updated,
                "categories": category_data,
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
