from djangoldp.views import LDPViewSet
from datetime import datetime
from .models import JobOffer


class JobOffersCurrentViewset(LDPViewSet):
    model = JobOffer

    def get_queryset(self):
        return super().get_queryset() \
                      .filter(closingDate__gte=datetime.now())


class JobOffersExpiredViewset(LDPViewSet):
    model = JobOffer

    def get_queryset(self):
        return super().get_queryset() \
                      .filter(closingDate__lte=datetime.now())

