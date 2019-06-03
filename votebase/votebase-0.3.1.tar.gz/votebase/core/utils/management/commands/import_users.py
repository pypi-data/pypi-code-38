import os
import csv

from django.contrib.auth import get_user_model
from progressbar import ProgressBar, Percentage, Bar

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError


User = get_user_model()


class Command(BaseCommand):
    args = '<csv_path>'
    help = 'Imports clients for specific user from CSV'
    # id,"username","first_name","last_name","email","password",is_staff,is_active,is_superuser,"last_login","date_joined"

    def handle(self, *args, **options):
        if not os.path.isfile(args[0]):
            raise CommandError('Import file does not exist!')

        users = csv.reader(open(args[0], 'rU'), delimiter=',', dialect=csv.excel)
        count = len(list(csv.reader(open(args[0], 'rU'), delimiter=',', dialect=csv.excel)))

        try:
            progress_bar = ProgressBar(widgets=[Percentage(), Bar()], maxval=int(count)).start()
            i = 0

            for user in users:
                progress_bar.update(i+1)
                try:
                    User.objects.get(username=user[1])
                    self.stdout.write('User %s already exists!\n' % user[1])
                    continue
                except ObjectDoesNotExist:
                    user = User.objects.create(
                        username=user[1],
                        first_name=user[2],
                        last_name=user[3],
                        email=user[4],
                        password=user[5],
                        is_staff=bool(user[6]),
                        is_active=bool(user[7]),
                        is_superuser=bool(user[8]),
                        last_login=user[9],
                        date_joined=user[10],
                    )

                    user.save()
                    i += 1

            progress_bar.finish()

            self.stdout.write('Successfully imported %(imported)i users from %(total)i.\n\n' % {
                'imported': i,
                'total': count,
            })

        except csv.Error:
            raise CommandError('Can not parse CSV!')
