# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from dc17.models.attendee import Attendee

SUBJECT = ('[ACTION REQUIRED]: Are you coming to DebConf17? '
           'Confirm your attendance *now*!')

TXT = """\
Dear %(name)s,

Our records indicate that you haven't confirmed your attendance at DebConf17.

The deadline to confirm is July 15 23:59 UTC. After this date, we cannot
guarantee any accommodation or food that you may have requested. Your badge
won't be printed and we probably won't have a t-shirt or swag to offer you
either.

If you want to confirm, simply log into the DebConf17 website, bring up your
profile through the upper right hand side menu and select "Update
Registration". On page 3 of that form, check "I confirm my attendance", then go
through the rest of the form verifying your data and Save.

If you know you're not going to be attending, please click the "Unregister"
link in your profile page.

Thank you,
The DebConf17 Registration Team
"""


class Command(BaseCommand):
    help = 'Badger users for confirmation'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),

    def badger(self, attendee, dry_run):
        to = attendee.user.email
        if dry_run:
            print('I would badger: %s <%s>' % (
                attendee.user.userprofile.display_name(),
                to,
            ))
            return

        body = TXT % {
            'name': attendee.user.userprofile.display_name(),
        }
        email_message = EmailMultiAlternatives(SUBJECT, body, to=[to])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        for attendee in Attendee.objects.filter(reconfirm=False):
            self.badger(attendee, dry_run)
