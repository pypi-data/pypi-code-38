from django.conf import settings

def expose_time_zone(request):
    return {'TIME_ZONE': settings.TIME_ZONE}
