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
import re
from datetime import datetime
from logging import getLogger
from typing import List
from quartet_epcis.models import events, entries, choices, headers
from quartet_epcis.parsing.business_parser import BusinessEPCISParser
from EPCPyYes.core.v1_2 import template_events as yes_events, events
from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import \
    InstanceLotMasterDataAttribute, \
    LotLevelAttributeName, \
    ItemLevelAttributeName, \
    TradeItemLevelAttributeName

from EPCPyYes.core.v1_2 import template_events
from quartet_output.parsing import BusinessOutputParser
from quartet_integrations.optel.epcpyyes import get_default_environment

logger = getLogger(__name__)
ilmd_list = List[yes_events.InstanceLotMasterDataAttribute]
# https://regex101.com/r/D1coNK/1
time_regex = re.compile(r'([\+\-]([01]\d|2[0-3]):([0-5]\d)|24:00)')


class OptelOutputEPCISParser(BusinessOutputParser):

    def get_epcpyyes_object_event(self):
        return template_events.ObjectEvent(
            epc_list=[], quantity_list=[],
            env=get_default_environment(),
            template='quartet_integrations/optel/object_event.xml'
        )

class OptelEPCISLegacyParser(BusinessEPCISParser):
    """
    Parses the old Optel non-compliant epcis data and converts
    to use-able EPCIS data for QU4RTET.
    """

    def parse(self, replace_timezone=False):
        """
        Will begin the parsing process of any inbound stream/file provided
        in the constructor.
        :param replace_timezone: Whether or not to replace timezones in
        event times with the timezone offset in the event.
        :return:
        """
        self._replace_timezone = replace_timezone
        return super().parse()

    def parse_unexpected_obj_element(self, oevent: yes_events.ObjectEvent,
                                     child):
        """
        Parses the optel ILMD elements that fall inside
        the standard object events.
        :param oevent: The object event EPCPyYes object.
        :param child:
        :return:
        """
        ilmd = None
        if child.tag.endswith('lotNumber'):
            ilmd = InstanceLotMasterDataAttribute(
                ItemLevelAttributeName.lotNumber.value,
                child.text.strip()
            )
        elif child.tag.endswith('itemExpirationDate'):
            ilmd = InstanceLotMasterDataAttribute(
                LotLevelAttributeName.itemExpirationDate.value,
                child.text.strip()
            )
        elif child.tag.endswith('unitOfMeasure'):
            ilmd = InstanceLotMasterDataAttribute(
                ItemLevelAttributeName.measurementUnitCode.value,
                child.text.strip()
            )
        elif child.tag.endswith('additionalTradeItemIdentificationValue'):
            ilmd = InstanceLotMasterDataAttribute(
                TradeItemLevelAttributeName
                    .additionalTradeItemIdentification.value,
                child.text.strip()
            )
        elif child.tag.endswith('additionalTradeItemIdentification'):
            for sub_element in child:
                self.parse_unexpected_obj_element(oevent, sub_element)
        if ilmd:
            oevent.ilmd.append(ilmd)

    def get_event_time(self, epcis_event: events.EPCISEvent) -> datetime:
        if self._replace_timezone and epcis_event.event_timezone_offset:
            epcis_event.event_time = time_regex.sub(
                epcis_event.event_timezone_offset,
                epcis_event.event_time
            )
            if epcis_event.record_time:
                epcis_event.record_time = time_regex.sub(
                    epcis_event.event_timezone_offset,
                    epcis_event.record_time
                )
        return super().get_event_time(epcis_event)

    def _parse_date(self, epcis_event):
        return self.get_event_time(epcis_event)


class ConsolidationParser(OptelEPCISLegacyParser):
    """
    Will condense the insane optel single object event per
    serial number into a single object event.  Only use this
    when you are sure that the structure of the lot messages
    is suitable.
    """

    def __init__(self, stream, event_cache_size: int = 1024,
                 recursive_decommission: bool = True):
        super().__init__(stream, event_cache_size, recursive_decommission)
        self.add_event = None
        self.db_event = None

    def handle_object_event(self, epcis_event: yes_events.ObjectEvent):
        if epcis_event.action == 'ADD':
            if self.add_event:
                # self.add_event.epc_list += epcis_event.epc_list
                self.handle_entries(self.db_event, epcis_event.epc_list,
                                    epcis_event)
                db_entries = self._get_entries(self.add_event.epc_list)
                self._update_event_entries(db_entries, self.db_event,
                                           epcis_event)
            else:
                logger.debug('Handling an ObjectEvent...')
                if not self.db_event:
                    self.db_event = self.get_db_event(epcis_event)
                    self.db_event.type = choices.EventTypeChoicesEnum.OBJECT.value
                self.handle_entries(self.db_event, epcis_event.epc_list,
                                    epcis_event)
                self.handle_common_elements(self.db_event, epcis_event)
                self.handle_ilmd(self.db_event.id, epcis_event.ilmd)
                self._append_event_to_cache(self.db_event)
                self.add_event = epcis_event
                db_entries = self._get_entries(self.add_event.epc_list)
                self._update_event_entries(db_entries, self.db_event,
                                           self.add_event)
        else:
            super().handle_object_event(epcis_event)
