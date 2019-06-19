from django.contrib import admin
from .models import RoadTripProfile, RoadTrip, Vehicle, RefuelEvent, StopEvent, SleepEvent

admin.site.register(RoadTripProfile)
admin.site.register(RoadTrip)
admin.site.register(Vehicle)
admin.site.register(RefuelEvent)
admin.site.register(StopEvent)
admin.site.register(SleepEvent)
