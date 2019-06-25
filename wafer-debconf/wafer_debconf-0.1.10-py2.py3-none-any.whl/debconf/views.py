from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.generic import TemplateView, View

from wafer.talks.models import Track
from wafer.schedule.views import ScheduleView
from wafer.schedule.models import Venue, ScheduleItem, Slot

from front_desk.models import CheckIn


class DCScheduleArrived(View):
    def arrived_users(self):
        queryset = CheckIn.objects.select_related(
            'attendee',
            'attendee__user',
            'attendee__user__userprofile',
        )
        for check_in in queryset.filter(attendee__announce_me=True):
            attendee = check_in.attendee
            user = attendee.user
            yield {
                'username': user.username,
                'name': user.userprofile.display_name(),
                'nick': attendee.nametag_3,
            }

    def get(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        auth = auth_header.split(None, 1)
        if not constant_time_compare(auth, ['Bearer', settings.DCSCHEDULE_TOKEN]):
            raise PermissionDenied('Missing/Invalid Authorization token')
        return JsonResponse({
            'arrived': list(self.arrived_users())
        })


class RobotsView(TemplateView):
    template_name = 'debconf/robots.txt'
    content_type = 'text/plain; charset=UTF-8'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SANDBOX'] = settings.SANDBOX
        return context


class DebConfScheduleView(ScheduleView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = Track.objects.all()
        return context


def get_current_slot():
    now = timezone.now()
    tz = timezone.get_default_timezone()

    for slot in Slot.objects.all():
        start = timezone.make_aware(slot.get_start_datetime(), tz)
        end = timezone.make_aware(slot.get_end_datetime(), tz)
        if start <= now and now < end:
            return slot


class IndexView(TemplateView):
    template_name = 'wafer/index.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)

        venues = Venue.objects.filter(
            notes__icontains='has video coverage'
        )

        venue_blocks = [{'venue': venue} for venue in venues]

        current_slot = get_current_slot()
        if current_slot:
            events = ScheduleItem.objects.filter(slots=current_slot)
            for event in events:
                for blk in venue_blocks:
                    if event.venue == blk['venue']:
                        slots = list(event.slots.all())
                        blk['event'] = event
                        blk['start_time'] = slots[0].get_formatted_start_time()
                        blk['end_time'] = slots[-1].get_formatted_end_time()

        context_data['venue_blocks'] = venue_blocks

        return context_data
