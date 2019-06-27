from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import ( AllowAny, IsAuthenticated )
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .serializers import TermsAndCondtionsDestailSerializer
from ..models import TermsAndConditions


class TermsAndConditionsDetailAPIView(RetrieveAPIView):
    serializer_class = TermsAndCondtionsDestailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return TermsAndConditions.objects.active().last()
