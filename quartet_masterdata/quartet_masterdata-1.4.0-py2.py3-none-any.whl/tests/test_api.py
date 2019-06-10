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
import json
import os
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import Group, User
from quartet_epcis.parsing.parser import QuartetParser
from quartet_masterdata.management.commands.create_masterdata_groups import \
    Command


class APITests(APITestCase):
    def setUp(self):
        from tests import factories
        location_type = factories.LocationTypeFactory.create()
        location = factories.LocationFactory.create()
        location2 = factories.LocationFactory.create(
            name='test',
            latitude=12.232,
            longitude=33.2343,
            GLN13="2345234523454",
            SGLN="urn:epc:id:sgln:23452.3452345.0",
        )
        location_field = factories.LocationFieldFactory.create(
            location=location)
        location_identifier = factories.LocationIdentifierFactory.create(
            identifier='urn:epc:id:sgln:305555.123456.2',
            identifier_type='SGLN',
            description='Second Base',
            location=location
        )
        self.setup_user()

    def setup_user(self):
        Command().handle()
        user = User.objects.create_user(username='testuser',
                                        password='unittest',
                                        email='testuser@seriallab.local')
        group = Group.objects.get(name='Master Data Access')
        user.groups.add(group)
        user.save()
        self.client.force_authenticate(user=user)
        self.user = user

    def test_location_by_id(self):
        url = reverse('location-by-identifier',
                      kwargs={'identifier': 'urn:epc:id:sgln:305555.123456.0'}
                      )
        result = self.client.get(url, format='json')
        self.assertEqual(result.status_code, 200)
        # print(result.data)

    def test_entry_geohistory(self):
        url = reverse(
            'entry-geohistory-by-epc',
            kwargs={'epc': 'urn:epc:id:sgtin:305555.0555555.1'}
        )
        result = self.client.get(url, format='json')
        self.assertEqual(result.status_code, 200)
        print(result.data)

    def _parse_test_data(self):
        curpath = os.path.dirname(__file__)
        parser = QuartetParser(
            os.path.join(curpath, 'data/epcis.xml')
        )
        message_id = parser.parse()
        print(parser.event_cache)
        parser.clear_cache()
        return message_id
