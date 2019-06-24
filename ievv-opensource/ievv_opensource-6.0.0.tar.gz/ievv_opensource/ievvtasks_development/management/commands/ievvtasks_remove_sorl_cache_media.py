import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Remove the sorl-thumbnail cache media directory if there is one.'

    def handle(self, *args, **options):
        thumbnail_prefix = getattr(settings, 'THUMBNAIL_PREFIX', None)
        if thumbnail_prefix:
            cache_directory = os.path.join(settings.MEDIA_ROOT, thumbnail_prefix)
            if os.path.exists(cache_directory):
                shutil.rmtree(cache_directory)
                self.stdout.write('Removed sorl-cache directory: {}'.format(
                    cache_directory))
            else:
                self.stdout.write('Sorl-cache directory does not exist: {}'.format(
                    cache_directory))
