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
import os
import django
from django.contrib.auth.models import Group, User
from django.db.models import Q
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()
from EPCPyYes.core.v1_2.events import EventType
from EPCPyYes.core.v1_2.CBV.dispositions import Disposition
from EPCPyYes.core.v1_2.CBV.business_steps import BusinessSteps
from rest_framework.test import APITestCase
from django.urls import reverse
from quartet_output import models
from quartet_output.management.commands.create_output_groups import Command

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()


class ViewTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser',
                                        password='unittest',
                                        email='testuser@seriallab.local')
        Command().handle()
        oag = Group.objects.get(name='Output Access')
        user.groups.add(oag)
        user.save()
        self.client.force_authenticate(user=user)
        self.user = user

    def test_endpoint(self):
        self._create_endpoint()
        url = reverse('end-points-list')
        response = self.client.get(url)
        self.assertIs(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('name'), 'Test EndPoint')

    def test_authentication_info(self):
        self._create_auth()
        url = reverse('authentication-info-list')
        response = self.client.get(url)
        self.assertIs(response.status_code, 200)

    def test_epcis_output_criteria(self):
        self._create_good_ouput_criterion()
        url = reverse('epcis-output-criteria-list')
        response = self.client.get(url)
        self.assertIs(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('action'), 'ADD')

    def test_read_only_epcis_output_criteria(self):
        self._create_good_ouput_criterion()
        url = reverse('read-only-epcis-output-criteria-list')
        response = self.client.get(url)
        self.assertIs(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('action'), 'ADD')

    def _create_good_ouput_criterion(self):
        endpoint = self._create_endpoint()
        auth = self._create_auth()
        eoc = models.EPCISOutputCriteria()
        eoc.name = "Test Criteria"
        eoc.action = "ADD"
        eoc.event_type = EventType.Transaction.value
        eoc.disposition = Disposition.in_transit.value
        eoc.biz_step = BusinessSteps.shipping.value
        eoc.biz_location = 'urn:epc:id:sgln:305555.123456.0'
        eoc.read_point = 'urn:epc:id:sgln:305555.123456.12'
        eoc.source_type = 'urn:epcglobal:cbv:sdt:location'
        eoc.source_id = 'urn:epc:id:sgln:305555.123456.12'
        eoc.destination_type = 'urn:epcglobal:cbv:sdt:location'
        eoc.destination_id = 'urn:epc:id:sgln:309999.111111.233'
        eoc.authentication_info = auth
        eoc.end_point = endpoint
        eoc.save()
        return eoc

    def _create_endpoint(self):
        ep = models.EndPoint()
        ep.urn = 'http://testhost'
        ep.name = 'Test EndPoint'
        ep.save()
        return ep

    def _create_auth(self):
        auth = models.AuthenticationInfo()
        auth.description = 'Unit test auth.'
        auth.username = 'UnitTestUser'
        auth.password = 'UnitTestPassword'
        auth.save()
        return auth

    def _get_test_data(self):
        '''
        Loads the XML file and passes its data back as a string.
        '''
        curpath = os.path.dirname(__file__)
        data_path = os.path.join(curpath, 'data/epcis.xml')
        with open(data_path) as data_file:
            return data_file.read()
