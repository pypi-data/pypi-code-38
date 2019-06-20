import csv

from django.core.management.base import BaseCommand

from dc17.models import Attendee, Food


class Command(BaseCommand):
    help = 'Output a CSV dump of nametag data'

    def handle(self, *args, **options):
        w = csv.writer(self.stdout)
        w.writerow(
            ('Name', 'Line 2', 'Line 3', 'Languages', 'Diet'))
        for attendee in Attendee.objects.all():
            try:
                diet = attendee.food.diet
            except Food.DoesNotExist:
                diet = ''

            w.writerow((
                attendee.user.userprofile.display_name(),
                attendee.nametag_2,
                attendee.nametag_3,
                attendee.languages,
                diet,
            ))
