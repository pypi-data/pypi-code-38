from django.core.management.base import BaseCommand, CommandError
from djangoldp_account.factories import ChatProfileFactory, AccountFactory
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Mock data'

    def handle(self, *args, **options):
        for user in User.objects.filter(account__isnull=True):
            AccountFactory.create(user=user);

        for user in User.objects.filter(chatProfile__isnull=True):
            ChatProfileFactory.create(user=user);

        self.stdout.write(self.style.SUCCESS('Successful data mock install'))
