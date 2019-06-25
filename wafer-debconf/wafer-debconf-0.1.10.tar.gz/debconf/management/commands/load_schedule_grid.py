from datetime import time
from django.conf import settings
from django.core.management.base import BaseCommand

from wafer.schedule.models import Venue, Day, Slot

import yaml


def parse_time(s):
    h, m = s.split(':')
    return time(int(h), int(m))


class Command(BaseCommand):
    help = 'Load Schedule days, venues, and slots from YAML files into the DB'

    def add_arguments(self, parser):
        parser.add_argument('YAMLFILE', help='Input file'),

    def handle(self, *args, **options):
        with open(options['YAMLFILE']) as f:
            data = yaml.safe_load(f)

        days = {}
        for datestr in data['days']:
            day, _ = Day.objects.get_or_create(date=datestr)
            days[datestr] = day
            print('Loaded day: %s' % day)

        for v in data['venues']:
            venue_name = v['name']
            venue, _ = Venue.objects.get_or_create(name=venue_name)
            venue.notes = v['notes']
            venue.order = v['order']
            venue_days = [day for d, day in days.items() if d in v['days']]
            venue.days = venue_days
            venue.save()
            print('Loaded venue: %s (%r)' % (venue, venue_days))

        for date, slots in data['slots'].items():
            day = days[date]
            for slotdata in slots:
                slot, _ = Slot.objects.get_or_create(day=day, name=slotdata['name'])
                slot.start_time = parse_time(slotdata['start'])
                slot.end_time = parse_time(slotdata['end'])
                slot.save()
                print('Loaded slot: %s' % slot)



