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

from django.db.models import Q
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from quartet_epcis.models import entries, events, headers


class Command(BaseCommand):
    help = _('Creates the default EPCIS access groups.')

    def handle(self, *args, **options):
        print('Creating the EPCIS Access group...')
        group, created = Group.objects.get_or_create(
            name='EPCIS Access'
        )
        if created:
            permissions = Permission.objects.filter(
                Q(codename__endswith='_entry') |
                Q(codename__endswith='_entryevent') |
                Q(codename__endswith='_errordeclaration') |
                Q(codename__endswith='_event') |
                Q(codename__endswith='_documentidentification') |
                Q(codename__endswith='_businesstransaction') |
                Q(codename__endswith='_destination') |
                Q(codename__endswith='_source') |
                Q(codename__endswith='_instancelotmasterdata') |
                Q(codename__endswith='_message') |
                Q(codename__endswith='_partner') |
                Q(codename__endswith='_quantityelement') |
                Q(codename__endswith='_sbdh') |
                Q(codename__endswith='_sourceevent') |
                Q(codename__endswith='_transformationid') |
                Q(codename__endswith='_destinationevent')
            )
            group.permissions.set(permissions)
            print('EPCIS Access group created.')
        else:
            print('Group "EPCIS Access" already exists.')
