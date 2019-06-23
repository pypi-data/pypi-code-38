# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from mezzanine_sync_pages.sync_pages import SyncPagesController


class Command(BaseCommand):
    help = "Sync the content of local pages in the filesystem to Mezzanine"

    # ----------------------------------------------------------------------
    def handle(self, *args, **options):
        controller = SyncPagesController(
            settings.MEZZANINE_SYNC_PAGES_DESTINATION_PATH,
            self.stdout,
            self.stderr,
            options['verbosity'])
        try:
            controller.sync()
        except Exception as exc:
            if options['traceback']:
                raise

            raise CommandError("Unable to sync page contents: {}".format(exc))
