from .base import BakeryBase
from rest_framework.response import Response
from issuestracker.models import Category, Candidate, Issue, Story
from issuestracker.serializers.bakery.SiteMap import CombinedSerializer
from issuestracker.serializers.bakery.HomePage import (
    CategorySerializer,
    CandidateSerializer,
    StorySerializer,
)


class BakeryHome(BakeryBase):
    def get(self, request, format=None):
        last_updated_category = Category.objects.order_by(
            "-last_published"
        ).first()
        last_updated_issue = Issue.objects.order_by("-last_published").first()

        last_updated = self.get_last_updated(
            last_updated_category, last_updated_issue
        )

        return Response(
            {
                "last_updated": last_updated,
                "categories": CategorySerializer(
                    Category.live.all(), many=True
                ).data,
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
