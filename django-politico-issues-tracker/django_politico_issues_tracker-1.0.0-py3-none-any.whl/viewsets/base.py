from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from issuestracker.utils.api_auth import TokenAPIAuthentication


class TokenAuthedViewSet(ModelViewSet):
    """
    ViewSet class that restricts views to our bots token.
    Also disables the default pagination.
    """

    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = (IsAuthenticated,)


class ReadOnlyTokenAuthedViewSet(ReadOnlyModelViewSet):
    """
    Read only ViewSet class that restricts views to our bots token.
    Also disables the default pagination.
    """

    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = (IsAuthenticated,)
