# This program is free software: you can redistribute it |/or modify
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

from django.contrib.auth.models import Permission, Group
from django.db.models import Q
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = 'Creates the default user group for master data access.'

    def handle(self, *args, **options):
        print('Creating group...')
        group, created = Group.objects.get_or_create(
            name='Master Data Access'
        )
        if created:
            permissions = Permission.objects.filter(
                Q(codename__endswith='_location') |
                Q(codename__endswith='_authenticationinfo') |
                Q(codename__endswith='_endpoint')
            )
            group.permissions.set(permissions)
            group.save()
            print('Group created.')
        else:
            print('Group already exists.')
