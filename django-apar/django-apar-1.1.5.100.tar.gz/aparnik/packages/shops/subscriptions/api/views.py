from rest_framework.permissions import ( AllowAny, IsAuthenticated )
from rest_framework.generics import ListAPIView

from aparnik.contrib.basemodels.api.serializers import ModelListPolymorphicSerializer
from ..models import Subscription


class SubscriptionListAPIView(ListAPIView):
    serializer_class = ModelListPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)

    def get_queryset(self, *args, **kwargs):
        return Subscription.objects.active()
