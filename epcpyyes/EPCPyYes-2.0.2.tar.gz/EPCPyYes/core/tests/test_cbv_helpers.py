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
# Copyright 2018 Rob Magee.  All rights reserved.

import unittest

from EPCPyYes.core.v1_2.CBV.helpers import make_trade_item_master_data_urn


class HelperTests(unittest.TestCase):
    '''
    Tests the various helpers defined in the CBV package.
    '''

    def test_trade_item_master_data_urn(self):
        '''
        Verifies that the trade item master data urns are created properly
        depending on whether they are instance or class level.  This is only
        for GTINs.
        :return:
        '''
        result = make_trade_item_master_data_urn('0355555', '23456', '1')
        self.assertEquals(result, 'urn:epc:idpat:sgtin:0355555.234561.*')
        result = make_trade_item_master_data_urn('0355555', '23456',
                                                 '1', serial_number='100023')
        self.assertEquals(result, 'urn:epc:id:sgtin:0355555.234561.100023')
        result = make_trade_item_master_data_urn('0355555', '23456',
                                                 '1', lot='LOT23')
        self.assertEquals(result, 'urn:epc:class:lgtin:0355555.234561.LOT23')
