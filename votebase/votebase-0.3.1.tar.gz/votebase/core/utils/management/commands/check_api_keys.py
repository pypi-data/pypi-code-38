from progressbar import ProgressBar, Percentage, Bar

from django.db.models import Q
from django.core.management.base import BaseCommand

from votebase.core.accounts.models import Profile


class Command(BaseCommand):

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(Q(api_key=None) | Q(api_key=''))
        total = profiles.count()
        if total == 0:
            print 'All profiles are good'
            return

        progress_bar = ProgressBar(widgets=[Percentage(), Bar()], maxval=int(total)).start()

        for index, profile in enumerate(profiles):
            progress_bar.update(index)
            profile.save()
        progress_bar.finish()
        print 'Successfully updated %d profiles.' % total
