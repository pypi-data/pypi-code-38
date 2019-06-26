from django.core.management.base import BaseCommand, CommandError
from djangoldp_profile.factories import ProfileFactory
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Mock data'

    def handle(self, *args, **options):
        for user in User.objects.filter(profile__isnull=True):
            ProfileFactory.create(user=user);

        self.stdout.write(self.style.SUCCESS('Successful data mock install'))
