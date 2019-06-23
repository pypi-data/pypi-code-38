# -*- coding: utf-8 -*-


from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.core.management import call_command

User = get_user_model()


class Command(BaseCommand):
    # Show this when the user types help
    help = "handle update"

    # A command must define handle()
    def handle(self, *args, **options):

        start_time = now()

        # handle course
        call_command('courseindexing')

        call_command('reviewssummary')

        call_command('progresssummary')

        call_command('notifiesme')

        call_command('sendnotifications')

        call_command('checkpayments')

        call_command('modelvisitupdate')

        finished_time = now()

        print(('handle objects update %s - time long: %ss.' % (now(), relativedelta(finished_time, start_time).seconds)))
