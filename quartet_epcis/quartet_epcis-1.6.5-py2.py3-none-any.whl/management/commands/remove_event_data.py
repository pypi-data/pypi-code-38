# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from quartet_epcis.models import entries, events, headers


class Command(BaseCommand):
    help = _('Clears out the event data.  For testing and debug systems only.')
    def add_arguments(self, parser):
        parser.add_argument('--force',
                            dest='force',
                            help='Force the removal of the event data.'
                            )
    def handle(self, *args, **options):
        debug = getattr(settings, 'DEBUG', False)
        force = options.get('force', False)
        if debug or force in ['True', 'true', 'TRUE']:
            print('Clearing out event data.')
            entries.Entry.objects.all().delete()
            events.Event.objects.all().delete()
            entries.EntryEvent.objects.all().delete()
            headers.Message.objects.all().delete()
            headers.SBDH.objects.all().delete()
            headers.Partner.objects.all().delete()
            headers.DocumentIdentification.objects.all().delete()
            print('Done.')
        else:
            print('Not valid on non-debug systems.')
