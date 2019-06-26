import os
from django.conf import settings
from django.core import management
import shutil
from django.test import TestCase


class TestRemoveSorlCacheMedia(TestCase):
    def setUp(self):
        self.thumbnail_prefix = 'test_sorlcache_dir'
        self.cachedir = os.path.join(settings.MEDIA_ROOT, self.thumbnail_prefix)
        if os.path.exists(self.cachedir):
            # This is not executed unless you run the tests multiple times
            # so we exclude it from coverage.
            shutil.rmtree(self.cachedir)  # pragma: no cover

    def test_no_cache_directory(self):
        with self.settings(THUMBNAIL_PREFIX=self.thumbnail_prefix):
            management.call_command('ievvtasks_remove_sorl_cache_media')

    def test_remove_existing_directory(self):
        os.makedirs(self.cachedir)
        open(os.path.join(self.cachedir, 'test.txt'), 'wb').write(b'test')
        with self.settings(THUMBNAIL_PREFIX=self.thumbnail_prefix):
            management.call_command('ievvtasks_remove_sorl_cache_media')
        self.assertFalse(os.path.exists(self.cachedir))
