# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from dc17.models.attendee import Attendee


SUBJECT = u'Your accommodation request for DebConf17'
TXT = u"""Hi,

Your registration profile for DebConf17 indicates that you have requested
on-site accommodation for your stay.

If you've already looked into this accommodation arrangement by reading the
information on the wiki [1], and you have no questions or concerns, then no
further action is required on your part.

However, if you've delayed looking into your accommodation details, then please
do so now.

If you find that the on-site arrangement of shared classroom dorms is not
adequate for you, please modify your registration profile and select
alternative accommodation (page 7, "I would like to request alternative
accommodation" checkbox). Doing this will have no effect on your bursary
application.

*After May 31st, we will consider your accommodation choice as final. We will
not be able to satisfy any last-minute re-accommodation requests.*

We want to ensure everyone has a most pleasant stay, so if you have any
question or concerns, please get in touch with us.

The DebConf registration team

[1] https://wiki.debconf.org/wiki/DebConf17/Accommodation#On-site
"""


class Command(BaseCommand):
    help = 'Send an email about making final accomm choices'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')

    def badger(self, attendee, dry_run):
        if dry_run:
            user_profile = attendee.user.userprofile
            print('I would badger: %s'
                  % user_profile.display_name().encode('utf-8'))
            return
        to = attendee.user.email
        email_message = EmailMultiAlternatives(SUBJECT, TXT, to=[to])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        for attendee in Attendee.objects.filter(
                accomm__isnull=False,
                user__bursary__request_accommodation=True):
            if not attendee.accomm.nights.exists():
                continue

            self.badger(attendee, dry_run)
