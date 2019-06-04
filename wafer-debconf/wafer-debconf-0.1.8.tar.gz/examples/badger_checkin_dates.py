# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from dc17.models import Accomm

ACCOMM_CHOICE_LABELS = {
    '': 'On-site dormitories',
    'rvc_single': 'Single room at McGill residences',
    'rvc_double': 'Double room at McGill residences',
    'hotel': 'Room at the Hôtel Universel',
}

SUBJECT = "Check-in and check-out dates for your DebConf 17 accommodation"

TEMPLATE = """\
Dear {name},

DebCamp and DebConf are approaching fast, and we have finalized the details
regarding accommodation during the conference. Here is what our reservation
records show for you:

{accommodation_details}

As a reminder, here are the details for the different accommodation options:
https://wiki.debconf.org/wiki/DebConf17/Accommodation

Cheers,
The DebConf Registration Team
"""

ON_SITE_MESSAGE = """\
Room assignations for the on-site dormitories are still in progress. We will
let you know as soon as the sorting hat decides on your roommates."""


def ascii_table(data, formats):
    col_width = [max(len(str(x)) for x in col) for col in zip(*data)]
    return "\n".join(
        ("| " + " | ".join(formats[i].format(x, col_width[i])
                           for i, x in enumerate(line)) + " |")
        for line in data
    )


class Command(BaseCommand):
    help = 'Badger users for confirmation'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),

    def badger(self, accomm, dry_run):
        name = accomm.attendee.user.get_full_name()
        to = accomm.attendee.user.email
        stays = list(accomm.get_stay_details())

        fmt = '%a %d %B %Y'

        stay_details = [
            (ACCOMM_CHOICE_LABELS.get(choice, 'On-site accommodation'),
             checkin.strftime(fmt), checkout.strftime(fmt))
            for checkin, checkout, choice in stays
        ]

        has_on_site = any(not(choice) for _, _, choice in stays)

        if dry_run:
            print('Would badger %s <%s> (%s) (%s)' %
                  (name, to, stay_details, has_on_site))
            return

        table_contents = [
            ('', 'Check-in', 'Check-out'),
        ] + stay_details

        accommodation_details = ascii_table(table_contents,
                                            ["{:{}}", "{:^{}}", "{:^{}}"])
        if has_on_site:
            accommodation_details += '\n\n%s' % ON_SITE_MESSAGE

        body = TEMPLATE.format(
            name=name,
            accommodation_details=accommodation_details,
        )

        email_message = EmailMultiAlternatives(SUBJECT, body,
                                               to=["%s <%s>" % (name, to)])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        for accomm in Accomm.objects.filter(attendee__reconfirm=True):
            self.badger(accomm, dry_run)
