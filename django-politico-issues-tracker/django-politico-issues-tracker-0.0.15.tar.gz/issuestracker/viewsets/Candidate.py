from .base import ReadOnlyTokenAuthedViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from issuestracker.models import Candidate
from issuestracker.serializers import CandidateSerializer


class CandidateViewset(ReadOnlyTokenAuthedViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    lookup_field = "slug"
    pagination_class = None
    throttle_classes = []

    @action(detail=False, methods=["get"])
    def by_slug(self, request, *args, **kwargs):
        output = {}
        for candidate in self.queryset:
            output[candidate.slug] = CandidateSerializer(candidate).data
        return Response(output)
