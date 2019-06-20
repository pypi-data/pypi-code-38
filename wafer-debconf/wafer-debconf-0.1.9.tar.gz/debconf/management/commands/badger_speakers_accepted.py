from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from wafer.talks.models import Talk


FROM = 'content@debconf.org'
SUBJECT = '%(conference)s - talk accepted: %(title)s'
BODY = '''\
Dear speaker / BoF organizer,

We are glad to announce that your activity titled
%(title)s
was accepted for presentation at %(conference)s.

We look forward to seeing you in %(city)s.
We will soon start to put the schedule together, so make sure that your arrival
and departure dates are up to date in the system, so we can schedule your
activity on a suitable date.

In case your plans changed and you won't be attending anymore, please let us
know by replying to this email, as soon as possible. Also, please cancel your
conference registration in the conference website.

Best regards,
The DebConf Content Team
'''


class Command(BaseCommand):
    help = "Notify speakers that their talks have been accepted"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),

    def badger(self, talk, dry_run):
        kv, _ = talk.kv.get_or_create(
            group=self.content_group,
            key='notified_speaker_accepted',
            defaults={'value': None},
        )

        if kv.value:
            return

        to = [user.email for user in talk.authors.all()]

        subst = {
            'title': talk.title,
            'conference': settings.DEBCONF_NAME,
            'city': settings.DEBCONF_CITY,
        }

        subject = SUBJECT % subst
        body = BODY % subst

        if dry_run:
            print('I would badger speakers of: %s' % talk.title)
            return
        email_message = EmailMultiAlternatives(
            subject, body, from_email=FROM, to=to)
        email_message.send()

        kv.value = True
        kv.save()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        self.content_group = Group.objects.get_by_natural_key('Talk Mentors')

        if dry_run:
            print('Not actually doing anything without --yes')

        for talk in Talk.objects.filter(status='A'):
            self.badger(talk, dry_run)
