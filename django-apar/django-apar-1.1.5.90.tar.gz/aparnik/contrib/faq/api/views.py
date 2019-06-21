from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import ( AllowAny, IsAuthenticated )

from .serializers import FAQDetailsSerializer
from ..models import FAQ


class FAQDetailAPIView(RetrieveAPIView):
    serializer_class = FAQDetailsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return FAQ.objects.active().last()
