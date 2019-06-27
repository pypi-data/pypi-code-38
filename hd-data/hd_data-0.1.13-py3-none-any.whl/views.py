from djangoldp.views import LDPViewSet
from datetime import datetime
from .models import Event

class FutureEventsViewset(LDPViewSet):
    model = Event
    def get_queryset(self):
        return super().get_queryset().filter(enddate__gte=datetime.now())