# -*- coding: utf-8 -*-
import datetime

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from django.template import Context, Template

from dc17.models.bursary import Bursary

DAYS_BEFORE = (6, 3, 1)

SUBJECT_TEMPLATE = Template("[Action needed] Your DebConf17 travel bursary "
                            "grant expires in {{days}} day{{days|pluralize}}!")
BODY_TEMPLATE = Template("""\
Dear {{object.user.get_full_name}},

Your travel bursary request has been granted by the bursaries team, and you
have not confirmed it yet.

You need to do so before {{ object.travel_accept_before|date }} at 23:59 UTC,
at which point the budget we have allocated for you will be redistributed to
other applicants.

Please log into the website at https://debconf17.debconf.org/bursary/ to update
your status.

If you're unable to do so before the deadline, let us know by replying to this
message and we'll work something out.

Thanks!
--\u0020
The DebConf Bursaries team
""")


class Command(BaseCommand):
    help = 'Send an email to people whose bursary grant expires soon'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually send emails')

    def badger(self, bursary, dry_run):
        context = {
            'object': bursary,
            'user': bursary.user.username,
        }

        delta = bursary.travel_accept_before - datetime.datetime.today().date()
        context['days'] = delta.days

        if dry_run:
            print('I would badger {user} (expiry in {days} days)'
                  .format(**context))
            return

        from_email = 'bursaries@debconf.org'
        to = bursary.user.email
        subject = SUBJECT_TEMPLATE.render(Context(context))
        body = BODY_TEMPLATE.render(Context(context))

        msg = EmailMultiAlternatives(subject, body, to=[to],
                                     from_email=from_email)

        msg.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        dates = [
            (datetime.datetime.today().date()
             + datetime.timedelta(days=days_before))
            for days_before in DAYS_BEFORE
        ]

        if dry_run:
            for date in dates:
                print('Will badger for expiry on %s' % date)

        to_badger = Bursary.objects.filter(
            request_travel=True,
            travel_status='pending',
            travel_accept_before__in=dates,
        )

        for bursary in to_badger:
            self.badger(bursary, dry_run)
