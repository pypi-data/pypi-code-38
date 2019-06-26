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
# Copyright 2019 SerialLab Corp.  All rights reserved.

from typing import List
from quartet_epcis.parsing.business_parser import BusinessEPCISParser
from EPCPyYes.core.v1_2 import events as yes_events

from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import \
    InstanceLotMasterDataAttribute, \
    LotLevelAttributeName, \
    ItemLevelAttributeName

ilmd_list = List[yes_events.InstanceLotMasterDataAttribute]


class SAPParser(BusinessEPCISParser):

    def parse_unexpected_obj_element(self, oevent, child):
        if child.tag == 'SAPExtension':
            for attribute_element in child:
                if 'objattributes' in attribute_element.tag.lower():
                    self.handle_sap_obj_attributes(oevent, attribute_element)

    def handle_sap_obj_attributes(self, oevent: yes_events.ObjectEvent,
                                  obj_attributes):
        """
        Parses the SAPExtension ObjAttributes node.
        :param oevent: The current EPCPyYes object event being constructed.
        :param obj_attributes: The ObjAttributes XML element.
        :return: None
        """
        for child in obj_attributes:
            if 'LOTNO' in child.tag:
                ilmd = InstanceLotMasterDataAttribute(
                    ItemLevelAttributeName.lotNumber.value,
                    value=child.text.strip())
                oevent.ilmd.append(ilmd)
            if 'DATEX' in child.tag:
                ilmd = InstanceLotMasterDataAttribute(
                    LotLevelAttributeName.itemExpirationDate.value,
                    value=child.text.strip()
                )
                oevent.ilmd.append(ilmd)
            if 'DATMF' in child.tag:
                ilmd = InstanceLotMasterDataAttribute(
                    'manufactureDate',
                    value=child.text.strip()
                )
                oevent.ilmd.append(ilmd)
