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
from datetime import datetime
from logging import getLogger
from dateutil.parser import parse as parse_date
from EPCPyYes.core.v1_2.CBV.business_steps import BusinessSteps
from EPCPyYes.core.v1_2.CBV.dispositions import Disposition
from EPCPyYes.core.v1_2.events import Action
from EPCPyYes.core.v1_2.events import AggregationEvent, ObjectEvent, \
    TransactionEvent
from gs123.conversion import BarcodeConverter
from quartet_epcis.models import Entry
from quartet_epcis.parsing.json import JSONParser as EPCISJSONParser
from quartet_masterdata.models import TradeItem, Company

logger = getLogger(__name__)


class JSONParser(EPCISJSONParser):
    """
    A class that pareses the oddly-formed divinci serial number format.
    """

    def __init__(self, stream, event_cache_size: int = 1024,
                 recursive_decommission: bool = True):
        self.master_material_cache = {}
        self.company_prefix_cache = {}
        super(JSONParser, self).__init__(stream, event_cache_size,
                                         recursive_decommission)

    def handle_aggregation_event(self, epcis_event: AggregationEvent):
        """
        Before the standard parser gets a chance to parse anything, we
        convert the malformed divinci urn values to valid GS1 values.
        :param epcis_event: The epcis event in question.
        :return: None
        """
        epcis_event.parent_id = self._convert_epc(epcis_event.parent_id)
        self._commission_new_parent(epcis_event)
        self._convert_epcs(epcis_event)
        self._dis_aggregate(epcis_event)
        self._create_shipment_event(epcis_event)
        return super().handle_aggregation_event(epcis_event)

    def _convert_epcs(self, epcis_event):
        """
        Convert the malformed EPC values into valid ones.
        :param epcis_event: The event with the bad values
        :return: None
        """
        new_epcs = []
        for epc in epcis_event.child_epcs:
            new_epcs.append(self._convert_epc(epc))
        epcis_event.child_epcs = new_epcs

    def _create_shipment_event(self, epcis_event):
        """
        Creates an actual shipment event.
        :param epcis_event: The inbound divinci event
        :return: None
        """
        xact = TransactionEvent(datetime.utcnow(),
                                '+00:00',
                                datetime.utcnow(),
                                parent_id=epcis_event.parent_id,
                                epc_list=epcis_event.child_epcs,
                                action=Action.observe.value,
                                biz_step=BusinessSteps.shipping.value,
                                disposition=Disposition.in_transit.value
                                )
        super().handle_transaction_event(xact)

    def _commission_new_parent(self, epcis_event):
        """
        If the parent does not exist, we auto-commission a new one.
        :param epcis_event: The inbound divinci event
        :return: None
        """
        if not Entry.objects.filter(identifier=epcis_event.parent_id).exists():
            obj_event = ObjectEvent(epcis_event.event_time,
                                    epcis_event.event_timezone_offset,
                                    epcis_event.record_time, Action.add.value)
            obj_event.epc_list.append(epcis_event.parent_id)
            obj_event.biz_step = BusinessSteps.commissioning.value,
            obj_event.disposition = Disposition.active
            self.handle_object_event(obj_event)

    def _dis_aggregate(self, epcis_event: AggregationEvent):
        """
        Does some magic to account for inadequacies in divinci.
        """
        for epc in epcis_event.child_epcs:
            # see if the child has a parent
            try:
                entry = Entry.objects.get(identifier=epc)
            except Entry.DoesNotExist:
                raise self.InvalidEPC('The EPC %s does not exist and can not'
                                      ' be processed.' % epc)
            # if so remove it
            if entry.parent_id:
                disagg = AggregationEvent(
                    datetime.utcnow(),
                    "+00:00",
                    datetime.utcnow(),
                    Action.delete.value,
                    biz_step=BusinessSteps.removing,
                    parent_id=entry.parent_id,
                )
                disagg.child_epcs.append(epc)
                super().handle_aggregation_event(disagg)

    def _convert_epc(self, epc: str) -> str:
        """
        Will convert the odd divincie gtin14.serialnumber format into a
        valid URN
        :param epc: The malformed divinci urn.
        :return: A properly formed gs1 epc urn.
        """
        if epc.startswith('urn:epc:id:sgtin:'):
            # split the string into gtin14 and serial number
            data = epc[17:].split('.')
            logger.debug('data = ', data)
            company_prefix_length = self._get_company_prefix_length(data[0])
            # create a "barcode" so we can use gs123 to convert to urn
            barcode_val = '(01)%s(21)%s' % (data[0], data[1])
            logger.debug('Converting barcode %s', barcode_val)
            converter = BarcodeConverter(
                barcode_val, company_prefix_length, len(data[1])
            )
            # Keep padded serial numbers from Da Vinci
            ret = converter.padded_epc_urn
        elif epc.startswith('urn:epc:id:sscc:'):
            barcode_val = epc[16:]
            company_prefix_length = self._get_company_prefix_length_sscc(
                barcode_val)
            converter = BarcodeConverter(barcode_val, company_prefix_length)
            ret = converter.epc_urn
        else:
            raise self.InvalidEncodingError(
                'The value %s did not have the proper URN prefix.  Only'
                ' sscc and gtin urn prefixes are supported.' % epc
            )
        return ret

    def _get_company_prefix_length_sscc(self, barcode_val: str) -> int:
        """
        Since there is no way to guess the length of the company prefix for
        an sscc we need to tap the database for it.
        """
        if len(barcode_val) != 20:
            raise self.SSCCError(
                'The length of the SSCC for the divinci parser must be 20 '
                'characters.'
            )
        for i in range(8, 18):
            current = barcode_val[3:i]
            logger.debug('Checking for a company prefix that starts with %s.')
            cache_cp = self.company_prefix_cache.get(current)
            if cache_cp:
                return cache_cp
            else:
                ssccs = Company.objects.filter(
                    gs1_company_prefix__startswith=current)
                if ssccs.count() > 1:
                    pass
                elif ssccs.count() == 1:
                    cp = ssccs[0].gs1_company_prefix
                    logger.debug('Found company prefix %s', cp)
                    self.company_prefix_cache[cp] = len(cp)
                    return len(cp)
                elif ssccs.count() == 0:
                    break
        raise self.SSCCError(
            'The SSCC %s did not have a correspoinding company entry '
            'associated with the company prefix.  Make sure there is '
            'a company record configured in master material with a '
            'company prefix that matches the one in the SSCC.' % barcode_val
        )

    def _get_company_prefix_length(self, gtin14: str) -> int:
        """
        Uses the GTIN 14 to look up the company prefix in quartet.
        :param gtin14: The gtin
        :return: The length of the company prefix record.
        """
        company_prefix_length = self.master_material_cache.get(gtin14)
        if not company_prefix_length:
            try:
                trade_item = TradeItem.objects.select_related().get(
                    GTIN14=gtin14)
                company_prefix_length = len(
                    trade_item.company.gs1_company_prefix)
                self.master_material_cache[
                    gtin14] = company_prefix_length
            except TradeItem.DoesNotExist:
                raise self.TradeItemConfigurationError(
                    'There is no trade item and corresponding company defined '
                    'for gtin %s.  This must be defined '
                    'in order for the system to '
                    'determin company prefix length. '
                    'Make sure you have a trade item configured and assigned to '
                    'a company that has a valid gs1 company prefix entry.' %
                    gtin14
                )
        return company_prefix_length

    def get_event_time(self, epcis_event) -> datetime:
        """
        Override to get a valid event time for a given event if you are
        dealing with non ISO or python date strings.
        :param epcis_event: The event with the event time to convert.
        :return: A datetime representing the EPCIS event event time string.
        """
        if epcis_event.event_timezone_offset in epcis_event.event_time:
            event_time = parse_date(epcis_event.event_time)
        else:
            event_time = parse_date("%sZ%s" % (
                epcis_event.event_time,
                epcis_event.event_timezone_offset))
        return event_time

    def _parse_date(self, epcis_event):
        return self.get_event_time(epcis_event)
    
    class TradeItemConfigurationError(Exception):
        pass

    class SSCCError(Exception):
        pass

    class InvalidEncodingError(Exception):
        pass

    class InvalidEPC(Exception):
        pass
