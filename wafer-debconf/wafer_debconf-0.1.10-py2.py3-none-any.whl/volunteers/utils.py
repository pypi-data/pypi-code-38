from datetime import timedelta
from django.utils import timezone


def get_start_end_for_scheduleitem(si):
    tz = timezone.get_default_timezone()
    if not si.slots.exists():
        raise ValueError('M2M not realized yet, come back later')
    start = timezone.make_aware(si.get_start_datetime(), tz)
    end = start + timedelta(minutes=si.get_duration_minutes())
    return (start, end)
