from rest_framework.views import APIView
from issuestracker.utils.api_auth import TokenAPIAuthentication
from issuestracker.models import Candidate
from issuestracker.serializers.Candidate import CandidateSerializer


class BakeryBase(APIView):
    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = []

    @staticmethod
    def get_last_updated(last_updated_category, last_updated_issue):

        last_updated_category_date = (
            last_updated_category.last_published
            if last_updated_category
            else None
        )

        last_updated_issue_date = (
            last_updated_issue.last_published
            if last_updated_category
            else None
        )

        if last_updated_category_date is None:
            if last_updated_issue_date is None:
                last_updated = None
            else:
                last_updated = last_updated_issue_date
        elif last_updated_issue_date is None:
            last_updated = last_updated_category_date
        else:
            last_updated = max(
                last_updated_category_date, last_updated_issue_date
            )

        if last_updated is not None:
            last_updated = last_updated.isoformat(" ")

        return last_updated

    def get_all_candidates(self):
        output = {}
        for candidate in Candidate.objects.all():
            output[candidate.slug] = CandidateSerializer(candidate).data
        return output
