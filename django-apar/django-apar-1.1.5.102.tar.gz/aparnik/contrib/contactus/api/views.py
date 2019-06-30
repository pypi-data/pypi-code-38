from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import ( AllowAny, IsAuthenticated )

from .serializers import ContactUsDestailSerializer
from ..models import ContactUs


class ContactUsListAPIView(ListAPIView):
    serializer_class = ContactUsDestailSerializer
    permission_classes = [IsAuthenticated]
    queryset = ContactUs.objects.active()


class ContactUsDetailAPIView(RetrieveAPIView):
    serializer_class = ContactUsDestailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_object(self):
        return ContactUs.objects.active()


class ContactUsCreateAPIView(CreateAPIView):
    serializer_class = ContactUsDestailSerializer
    permission_classes = [AllowAny]
    queryset = ContactUs.objects.active()
