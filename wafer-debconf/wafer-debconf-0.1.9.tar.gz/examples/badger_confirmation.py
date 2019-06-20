# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from dc17.models.attendee import Attendee
from dc17.models.bursary import Bursary

SUBJECT = {
    True: 'Please check and update your DebConf17 registration data',
    False: 'Please confirm your DebConf17 attendance',
}

TXT = {}

TXT[True] = """\
Hi,

DebConf17 is now closer than ever. Our records indicate that you have confirmed
that you will be coming to DebConf, either through the registration form or
through the bursaries confirmation process.

Please make sure that your data is correct in the registration page at:
https://debconf17.debconf.org/accounts/profile/

We need accurate data before July 16th: your arrival and departure dates are
what helps us for accommodation and food planning. If it turns out that you are
unable to attend, you need to use the "Unregister" form on the aforementioned
profile page.
"""

TXT[False] = """\
Hi,

DebConf17 is now closer than ever. It is time for the organizers to get a list
of who will actually be attending the conference, and to collect payment for
those of you who registered as paying attendees.

The confirmation and invoicing process uses the registration wizard
linked on your profile at: https://debconf17.debconf.org/accounts/profile/

To confirm your attendance, you need to set final arrival and departure dates,
select the "My dates are final" entry and tick the "I confirm my attendance"
box. You need to go through the wizard until the end for your confirmation to
be valid! This makes it a perfect time to review your full registration data.
"""

INVOICING = """\
If you registered as a self-paying attendee, the confirmation process will
generate an invoice including your registration fee, as well as your choice of
accommodation and food for the duration of the conference. Once generated, the
invoice will show up on your profile page, and you will be able to settle it
online through the Debian PayPal account managed by SPI.
"""

DATES_TEMPLATE = """\
We have you registered as:
Arriving on {arrival}
Departing on {departure}
"""

FOOTER = """\
See you in Montréal,
The DebConf Registration team
"""


class Command(BaseCommand):
    help = 'Badger users for confirmation'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),

    def badger(self, attendee, dry_run):
        to = attendee.user.email
        confirmed = attendee.reconfirm
        self_paying = True

        try:
            bursary = Bursary.objects.get(user=attendee.user)
        except Bursary.DoesNotExist:
            pass
        else:
            if bursary.request_accommodation:
                self_paying = False

        action_needed = not confirmed

        if dry_run:
            print('I would badger: %s <%s> (%s, %s, %s)' % (
                attendee.user.userprofile.display_name(),
                to,
                'action needed' if action_needed else 'no action needed',
                'self paying' if self_paying else 'sponsored',
            ))
            return

        subject = (('[Action Needed] ' if action_needed else '')
                   + SUBJECT[confirmed])

        body_parts = []
        body_parts.append(TXT[confirmed])
        if self_paying:
            body_parts.append(INVOICING)
        body_parts.append(DATES_TEMPLATE.format(arrival=attendee.arrival,
                                                departure=attendee.departure))
        body_parts.append(FOOTER)

        body = '\n'.join(body_parts)

        email_message = EmailMultiAlternatives(subject, body, to=[to])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        for attendee in Attendee.objects.all():
            self.badger(attendee, dry_run)
