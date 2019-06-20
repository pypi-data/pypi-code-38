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
from django.core.management.base import BaseCommand, CommandError
from quartet_output.management.commands.utils import create_output_filter_rule


class Command(BaseCommand):
    help = _(
        'Loads the quartet_output demonstration and transport rules into '
        'the database.'
    )

    def handle(self, *args, **options):
        create_output_filter_rule()
        create_output_filter_rule(rule_name='EPCIS Delayed Output Filter',
                                  delay_rule=True)

