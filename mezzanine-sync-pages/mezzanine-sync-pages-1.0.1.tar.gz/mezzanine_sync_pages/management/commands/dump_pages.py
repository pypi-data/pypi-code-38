# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

from django.conf import settings
from django.core.management import BaseCommand

from mezzanine_sync_pages.dump_pages import DumpPagesController


class Command(BaseCommand):
    help = "Dump the content of all Mezzanine pages to the filesystem"

    # ----------------------------------------------------------------------
    def handle(self, *args, **options):
        controller = DumpPagesController(
            settings.MEZZANINE_SYNC_PAGES_DESTINATION_PATH,
            self.stdout,
            options['verbosity'])
        controller.dump()
