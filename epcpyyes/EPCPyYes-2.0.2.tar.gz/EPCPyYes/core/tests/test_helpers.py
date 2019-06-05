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
# Copyright 2017 Serial Lab.  All rights reserved.

import unittest
from datetime import datetime
from EPCPyYes.core.v1_2 import helpers


class HelperTests(unittest.TestCase):
    '''
    Tests the various helpers defined in the v1_2 helpers package.
    '''

    def test_sscc_urn_generator(self):
        '''
        Verifies that the SSCC URN generator yields correctly formatted SSCC
        and the output matches the input. Checks the 0 padding is applied properly
        based on length of parameters that constitute the SSCC URN.
        '''
        results = list(helpers.sscc_urn_generator(company_prefix='1234567', extension='1',
                                          serial_numbers=['1', '2', '12345', '111111111']))
        self.assertEqual(results[0], 'urn:epc:id:sscc:1234567.1000000001')
        self.assertEqual(results[1], 'urn:epc:id:sscc:1234567.1000000002')
        self.assertEqual(results[2], 'urn:epc:id:sscc:1234567.1000012345')
        self.assertEqual(results[3], 'urn:epc:id:sscc:1234567.1111111111')
        results = list(helpers.sscc_urn_generator(company_prefix='123456', extension='2',
                                          serial_numbers=['1', '2', '12345', '1111111111', '111111111']))
        self.assertEqual(results[0], 'urn:epc:id:sscc:123456.20000000001')
        self.assertEqual(results[1], 'urn:epc:id:sscc:123456.20000000002')
        self.assertEqual(results[2], 'urn:epc:id:sscc:123456.20000012345')
        self.assertEqual(results[3], 'urn:epc:id:sscc:123456.21111111111')
        self.assertEqual(results[4], 'urn:epc:id:sscc:123456.20111111111')

    def test_iso_8601_helper(self):
        isodate = datetime.now().isoformat()
        regex = helpers.get_iso_8601_regex()
        res = regex.match(isodate)
        self.assertIsNotNone(res, 'The date regex is incorrect.')