from sys import exit
from django.core.management.base import BaseCommand

from wafer.schedule.admin import SCHEDULE_ITEM_VALIDATORS
from wafer.schedule.admin import SLOT_VALIDATORS
from wafer.schedule.admin import prefetch_schedule_items
from wafer.schedule.admin import prefetch_slots


class Command(BaseCommand):
    help = 'Validates the schedule and displays any issues'

    def handle(self, *args, **options):
        # This is a copy of wafer.schedule.admin.validate_schedule as submitted
        # in https://github.com/CTPUG/wafer/pull/468
        #
        # After/when that is merged and available in wafer, we can replace the
        # code below with a simple loop over the return value of
        # wafer.schedule.admin.validate_schedule.

        rc = 0

        all_items = prefetch_schedule_items()
        for validator, _type, msg in SCHEDULE_ITEM_VALIDATORS:
            for item in validator(all_items):
                print('%s: %s' % (msg, item))
                rc = 1

        all_slots = prefetch_slots()
        for validator, _type, msg in SLOT_VALIDATORS:
            for slot in validator(all_slots):
                print('%s: %s' % (msg, slot))
                rc = 1

        exit(rc)
