from collections import defaultdict
import csv
import datetime

from django.core.management.base import BaseCommand

from wafer.schedule.models import Day, Slot, Venue, ScheduleItem
from wafer.talks.models import Talk, CANCELLED, ACCEPTED


def parse_timestamp(timestamp):
    """Parse a timestamp into a usable datetime.datetime object"""
    hour, minute = timestamp.split(':')
    return datetime.datetime(1970, 1, 1, int(hour), int(minute))


def unparse_timestamp(dt):
    """Unparse a parsed timestamp"""
    return dt.time()


class Command(BaseCommand):
    help = 'Import schedule from a CSV grid'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--accept-talks', action='store_true',
                            help='Accept the talks that need accepting')
        parser.add_argument('file', help='CSV file')

    def parse_csv(self, csv):
        return

    def handle(self, *args, **options):
        do_it = options['yes']
        accept_talks = options['accept_talks']
        filename = options['file']
        with open(filename, 'r') as f:
            dialect = csv.Sniffer().sniff(f.read(4096))
            f.seek(0)
            data = list(csv.DictReader(f, dialect=dialect))

        rooms = [key for key in data[0] if key.startswith('room_')]
        room_map = {
            room: Venue.objects.get(pk=int(room[5:]))
            for room in rooms
        }
        slots = []
        talk_venue_slots = defaultdict(list)

        lineno = 0
        while lineno < len(data) - 1:
            half_hr_1 = data[lineno]
            half_hr_2 = data[lineno + 1]
            day = Day.objects.get(date__day=int(half_hr_1['day']))
            start_time_1 = parse_timestamp(half_hr_1['start_time'])
            start_time_2 = parse_timestamp(half_hr_2['start_time'])

            # Check whether the slot should be merged with the next one
            half_hour_slots = False
            for room in rooms:
                if not half_hr_1[room] and not half_hr_2[room]:
                    continue
                if half_hr_1[room] != half_hr_2[room]:
                    half_hour_slots = True

            if half_hour_slots:
                slot1, _ = Slot.objects.get_or_create(
                    day=day,
                    start_time=unparse_timestamp(start_time_1),
                    end_time=unparse_timestamp(
                        start_time_1 + datetime.timedelta(seconds=20*60)
                    ),
                    name='First Half Hour',
                )
                slot_middle, _ = Slot.objects.get_or_create(
                    day=day,
                    start_time=slot1.end_time,
                    end_time=unparse_timestamp(start_time_2),
                    name='Short Break',
                )
                slot2, _ = Slot.objects.get_or_create(
                    day=day,
                    start_time=slot_middle.end_time,
                    end_time=unparse_timestamp(
                        start_time_2 + datetime.timedelta(seconds=20*60)
                    ),
                    name='Second Half Hour',
                )
                slot_filler, _ = Slot.objects.get_or_create(
                    day=day,
                    start_time=slot2.end_time,
                    end_time=unparse_timestamp(
                        start_time_1 + datetime.timedelta(seconds=60*60)
                    ),
                    name='Less Short Break',
                )
                all_slots = [slot1, slot_middle, slot2, slot_filler]
                slots.extend(all_slots)

                for room in rooms:
                    if half_hr_1[room]:
                        talk_venue_slots[half_hr_1[room], room].extend(
                            (slot1, slot_middle)
                        )
                    if half_hr_2[room]:
                        talk_venue_slots[half_hr_2[room], room].extend(
                            (slot2, slot_filler)
                        )
            else:
                slot2, _ = Slot.objects.get_or_create(
                    day=day,
                    start_time=unparse_timestamp(start_time_1),
                    end_time=unparse_timestamp(
                        start_time_1 + datetime.timedelta(seconds=45*60)
                    ),
                    name='Full Hour',
                )
                slot_filler, _ = Slot.objects.get_or_create(
                    day=day,
                    start_time=slot2.end_time,
                    end_time=unparse_timestamp(
                        start_time_1 + datetime.timedelta(seconds=60*60)
                    ),
                    name='Less Short Break',
                )
                slots.append(slot2)
                slots.append(slot_filler)
                for room in rooms:
                    if not half_hr_1[room]:
                        continue
                    talk_venue_slots[half_hr_1[room], room].extend(
                        (slot2, slot_filler)
                    )

            print(day, half_hr_1, half_hr_2)

            lineno += 2

        for slot in slots:
            slot.clean()
            print(slot.day, slot.start_time, slot.end_time)
            if do_it:
                slot.save()

        for (talk, venue), slots in talk_venue_slots.items():
            talk = Talk.objects.get(pk=int(talk))
            print(talk, venue, slots)
            if do_it:
                s_i, _ = ScheduleItem.objects.get_or_create(
                    talk=talk, defaults={'venue': room_map[venue]}
                )
                s_i.venue = room_map[venue]
                s_i.clean()
                if accept_talks and talk.status not in (CANCELLED, ACCEPTED):
                    talk.status = ACCEPTED
                    talk.save()
                s_i.save()
                s_i.slots.set(slots[:-1])
                print(s_i, s_i.slots.all())
