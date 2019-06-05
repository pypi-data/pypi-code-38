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

import unittest
import json
import uuid
import re
from datetime import datetime

from EPCPyYes.core.errors import ValidationError
from EPCPyYes.core.v1_2.helpers import gtin_urn_generator, \
    get_current_utc_time_and_offset, gln13_data_to_sgln_urn, gtin_to_urn
from EPCPyYes.core.v1_2.events import BusinessTransaction, \
    Source, Destination, \
    Action, QuantityElement, ErrorDeclaration
from EPCPyYes.core.v1_2.template_events import ObjectEvent, AggregationEvent, \
    EPCISDocument, TransactionEvent, TransformationEvent, \
    EPCISEventListDocument
from EPCPyYes.core.v1_2.CBV.dispositions import Disposition
from EPCPyYes.core.v1_2.CBV.source_destination import SourceDestinationTypes
from EPCPyYes.core.v1_2.CBV.business_steps import BusinessSteps
from EPCPyYes.core.v1_2.CBV.business_transactions import \
    BusinessTransactionType
from EPCPyYes.core.v1_2.CBV.instance_lot_master_data import \
    InstanceLotMasterDataAttribute, \
    LotLevelAttributeName, ItemLevelAttributeName
from EPCPyYes.core.v1_2.CBV import helpers, error_reasons
from EPCPyYes.core.tests.test_utils import validate_epcis_doc
from EPCPyYes.core.SBDH import template_sbdh
from EPCPyYes.core.SBDH import sbdh
from EPCPyYes.core.v1_2.json_decoders import AggregationEventDecoder, \
    ObjectEventDecoder, TransactionEventDecoder


class CoreEventTests(unittest.TestCase):
    '''
    Tests serializing the core EPCIS classes using the template_events
    package classes.
    '''

    def test_gtin_helper(self):
        nums = range(1000, 1099)
        epcs = gtin_urn_generator('305555', '1', '555555', nums)
        for epc in epcs:
            i = 0
            i += 1
            if i == 0:
                self.assertEquals(epc, 'urn:epc:id:sgtin:305555.5555551.1000')
            elif i == 99:
                self.aseertEquals(epc, 'urn:epc:id:sgtin:305555.5555551.1098')

    def test_datetime_helper(self):
        '''
        Tests the datetime helper and examines the results to ensure
        compatibility with EPCIS event requirements for date-time values.

        :return: None
        '''
        vals = get_current_utc_time_and_offset()
        print(vals)
        # should be able to convert back
        datetime.strptime(vals[0], '%Y-%m-%dT%H:%M:%S.%f+00:00')
        # check regex on timezone
        match = re.search(r'[\+\-][0-9]{2}:[0-9]{2}', vals[1])
        self.assertIsNotNone(match)

    def test_aggregation_event_template(self):
        '''
        Creates an aggregation event and renders it using the
        aggregation event template.

        :return: String with the rendered event.
        '''

        epcs = self.create_epcs(1000, 1010)
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        # get the current time and tz
        ae = self.create_aggregation_event(epcs, parent_id)
        print(ae.render())
        print(ae.render_json())
        print(ae.render_pretty_json())
        reverse = json.loads(ae.render_json())
        print(reverse)

    def test_aggregation_event_json_decode(self):
        '''
        Creates an aggregation event and renders it using the
        aggregation event template.

        :return: String with the rendered event.
        '''

        epcs = self.create_epcs(1000, 1010)
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        # get the current time and tz
        ae = self.create_aggregation_event(epcs, parent_id)
        decoded = AggregationEventDecoder(ae.render_pretty_json()).get_event()
        self.assertEqual(ae.child_epcs, decoded.child_epcs)
        self.assertEqual(ae.parent_id, decoded.parent_id)
        self.assertEqual(ae.action, decoded.action)

    def test_object_event_json_decode(self):
        oe = self.create_object_event_template()
        # render the event using it's default template
        data = oe.render_pretty_json()
        decoded = ObjectEventDecoder(data).get_event()
        self.assertEqual(oe.action, decoded.action)
        self.assertEqual(oe.biz_step, decoded.biz_step)
        self.assertEqual(oe.disposition, decoded.disposition)
        print(decoded.render_pretty_json())

    def test_transaction_event_json_decode(self):
        epcs = self.create_epcs(1000, 1010)
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        te = self.create_transaction_event(epcs, parent_id)
        # render the event using it's default template
        decoded = TransactionEventDecoder(
            te.render_pretty_json()
        ).get_event()
        self.assertEqual(te.action, decoded.action)
        self.assertEqual(te.biz_step, decoded.biz_step)
        self.assertEqual(te.disposition, decoded.disposition)

    def test_bad_aggregation_event(self):
        '''
        Creates an aggregation event and renders it using the
        aggregation event template.

        :return: String with the rendered event.
        '''

        epcs = self.create_epcs(1000, 1010)
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        # get the current time and tz
        ae = self.create_aggregation_event(epcs, parent_id)
        ae.clean()  # should be good...
        ae.child_epcs = None
        ae.child_quantity_list = None
        self.assertRaises(ValidationError, ae.clean)
        ae = self.create_aggregation_event(epcs, None)
        ae.action = Action.add.value
        self.assertRaises(ValidationError, ae.clean)

    def test_transformation_event_template(self):
        '''
        Creates a Transformation E

        :return:
        '''
        te = self.create_transformation_event()
        print(te.render())
        print(te.render_json())
        print(te.render_pretty_json())

    def create_aggregation_event(self, epcs, parent_id):
        business_transaction_list = self.create_business_transaction_list()
        biz_location, read_point, source_list = self.create_source_list()
        destination_list = self.create_destination_list()
        trade_item = helpers.make_trade_item_master_data_urn('305555', '0',
                                                             '555551')
        child_quantity_list = [
            QuantityElement(epc_class=trade_item, quantity=100),
            QuantityElement(epc_class=trade_item, quantity=94.3,
                            uom='LB')]
        event_id = str(uuid.uuid4())
        error_declaration = self.create_error_declaration()
        ae = AggregationEvent(
            action=Action.add.value,
            parent_id=parent_id, child_epcs=epcs,
            business_transaction_list=business_transaction_list,
            biz_location=biz_location, read_point=read_point,
            source_list=source_list,
            destination_list=destination_list,
            child_quantity_list=child_quantity_list,
            error_declaration=error_declaration,
            event_id=event_id,
            biz_step=BusinessSteps.packing.value,
            record_time=datetime.now()
        )
        return ae

    def create_transaction_event(self, epcs, parent_id):
        now, tzoffset = get_current_utc_time_and_offset()
        business_transaction_list = self.create_business_transaction_list()
        biz_location, read_point, source_list = self.create_source_list()
        destination_list = self.create_destination_list()
        trade_item = helpers.make_trade_item_master_data_urn('305555', '0',
                                                             '555551')
        disposition = Disposition.in_transit.value
        biz_step = BusinessSteps.shipping.value
        quantity_list = [
            QuantityElement(epc_class=trade_item, quantity=100),
            QuantityElement(epc_class=trade_item, quantity=94.3,
                            uom='LB')]

        event_id = str(uuid.uuid4())
        error_declaration = self.create_error_declaration()

        te = TransactionEvent(
            now,
            tzoffset,
            now,
            action=Action.add.value,
            parent_id=parent_id,
            epc_list=epcs,
            business_transaction_list=business_transaction_list,
            biz_location=biz_location,
            read_point=read_point,
            source_list=source_list,
            destination_list=destination_list,
            biz_step=biz_step,
            disposition=disposition,
            event_id=event_id,
            error_declaration=error_declaration)
        te.quantity_list = quantity_list
        return te

    def create_sbdh(self):
        sender_partner_id = sbdh.PartnerIdentification(
            authority='SGLN',
            value='urn:epc:id:sgln:039999.999999.0'
        )
        receiver_partner_id = sbdh.PartnerIdentification(
            authority='SGLN',
            value='urn:epc:id:sgln:039999.111111.0'
        )
        sender = sbdh.Partner(
            partner_type=sbdh.PartnerType.SENDER,
            partner_id=sender_partner_id,
            contact='John Smith',
            telephone_number='555-555-5555',
            email_address='john.smith@pharma.local',
            contact_type_identifier='Seller'
        )
        receiver = sbdh.Partner(
            partner_type=sbdh.PartnerType.RECEIVER,
            partner_id=receiver_partner_id,
            contact='Joe Blow',
            telephone_number='555-555-2222',
            email_address='joe.blow@distributor.local',
            contact_type_identifier='Buyer'
        )
        document_identification = sbdh.DocumentIdentification(
            creation_date_and_time=datetime.now().isoformat(sep="T"),
            document_type=sbdh.DocumentType.EVENTS
        )
        header = template_sbdh.StandardBusinessDocumentHeader(
            document_identification=document_identification,
            partners=[sender, receiver]
        )
        self.assertEqual(sender_partner_id.value,
                         'urn:epc:id:sgln:039999.999999.0')
        self.assertEqual(sender_partner_id.authority, 'SGLN')
        self.assertEqual(receiver_partner_id.authority, 'SGLN')
        self.assertEqual(
            receiver_partner_id.value, 'urn:epc:id:sgln:039999.111111.0'
        )
        self.assertEqual(sender.partner_type, 'Sender')
        self.assertEqual(sender.contact, 'John Smith')
        self.assertEqual(sender.telephone_number, '555-555-5555')
        self.assertEqual(sender.email_address, 'john.smith@pharma.local')
        self.assertEqual(sender.contact_type_identifier, 'Seller')
        print(header.render())
        print(header.render_json())
        print(header.render_pretty_json())
        return header

    def test_object_event_template(self):
        oe = self.create_object_event_template()
        # render the event using it's default template
        data = oe.render()
        print(oe.render_json())
        print(oe.render_pretty_json())
        print(data)
        # make sure the data we want is there
        self.assertTrue('+00:00' in data)
        self.assertIn('<epc>urn:epc:id:sgtin:305555.1555555.1000</epc>', data,
                      'URN for start SGTIN not present.')
        self.assertIn('<epc>urn:epc:id:sgtin:305555.1555555.1001</epc>', data,
                      'URN for start SGTIN not present.')
        self.assertIn('<action>ADD</action>', data,
                      'EPCIS action not present.')
        self.assertIn(BusinessSteps.commissioning.value, data,
                      'Business step not present')
        self.assertIn(Disposition.encoded.value, data,
                      'Disposition not present')

    def test_transaction_event_template(self):
        epcs = self.create_epcs(1000, 1010)
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        te = self.create_transaction_event(epcs, parent_id)
        # render the event using it's default template
        data = te.render()
        print(te.render_json())
        print(te.render_pretty_json())
        print(data)
        # make sure the data we want is there
        self.assertTrue('+00:00' in data)
        self.assertIn('<epc>urn:epc:id:sgtin:305555.1555555.1000</epc>',
                      data,
                      'URN for start SGTIN not present.')
        self.assertIn('<epc>urn:epc:id:sgtin:305555.1555555.1001</epc>',
                      data,
                      'URN for start SGTIN not present.')
        self.assertIn('<action>ADD</action>', data,
                      'EPCIS action not present.')
        self.assertIn(BusinessSteps.shipping.value, data,
                      'Business step not present')
        self.assertIn(Disposition.in_transit.value, data,
                      'Disposition not present')

    def test_epcis_base_template(self):
        oe1 = self.create_object_event_template()
        oe2 = self.create_object_event_template()

        object_events = [oe1, oe2]
        ag1 = self.create_aggregation_event(self.create_epcs(1000, 1009),
                                            gtin_to_urn('305555', '2',
                                                        '555555', '235'))
        ag2 = self.create_aggregation_event(self.create_epcs(1010, 1019),
                                            gtin_to_urn('305555', '2',
                                                        '555555', '216'))
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        epcs = self.create_epcs(1000, 1010)
        transaction_event = self.create_transaction_event(epcs, parent_id)
        txe = self.create_transformation_event()
        header = self.create_sbdh()
        epcis_document = EPCISDocument(
            header=header,
            object_events=object_events,
            aggregation_events=[ag1, ag2],
            transaction_events=[transaction_event],
            transformation_events=[txe]
        )
        print(epcis_document.render())
        print(epcis_document.render_json())
        print(epcis_document.render_pretty_json())
        validate_epcis_doc(epcis_document.render().encode('utf-8'))
        return epcis_document

    def test_epcis_event_list_template(self):
        oe1 = self.create_object_event_template()
        oe2 = self.create_object_event_template()
        ag1 = self.create_aggregation_event(self.create_epcs(1000, 1009),
                                            gtin_to_urn('305555', '2',
                                                        '555555', '235'))
        ag2 = self.create_aggregation_event(self.create_epcs(1010, 1019),
                                            gtin_to_urn('305555', '2',
                                                        '555555', '216'))
        parent_id = gtin_to_urn('305555', '1', '555551', 1000)
        epcs = self.create_epcs(1000, 1010)
        transaction_event = self.create_transaction_event(epcs, parent_id)
        txe = self.create_transformation_event()
        template_events = [oe1, oe2, ag1, ag2, transaction_event, txe]
        header = self.create_sbdh()
        epcis_document = EPCISEventListDocument(
            header=header,
            template_events=template_events
        )
        print(epcis_document.render())
        print(epcis_document.render_json())
        print(epcis_document.render_pretty_json())
        validate_epcis_doc(epcis_document.render().encode('utf-8'))
        return epcis_document

    def test_transformation_doc(self):
        txe = self.create_transformation_event()
        epcis_document = EPCISDocument(transformation_events=[txe])
        print(epcis_document.render(render_xml_declaration=False))
        validate_epcis_doc(epcis_document.render().encode('utf-8'))

    def create_error_declaration(self):
        return ErrorDeclaration(
            reason=error_reasons.ErrorReason.incorrect_data.value,
            corrective_event_ids=[str(uuid.uuid4()), str(uuid.uuid4())]
        )

    def create_transformation_event(self):
        now, tzoffset = get_current_utc_time_and_offset()
        event_id = str(uuid.uuid4())
        error_declaration = self.create_error_declaration()
        input_epcs = self.create_epcs(1000, 1010)
        output_epcs = self.create_epcs(2000, 2010)
        business_transaction_list = self.create_business_transaction_list()
        biz_location, read_point, source_list = self.create_source_list()
        destination_list = self.create_destination_list()

        ilmd = [
            InstanceLotMasterDataAttribute(
                name=LotLevelAttributeName.itemExpirationDate.value,
                value='2015-12-31'),
            InstanceLotMasterDataAttribute(
                name=ItemLevelAttributeName.lotNumber.value,
                value='DL232')
        ]

        trade_item = helpers.make_trade_item_master_data_urn('305555', '0',
                                                             '555551')
        output_quantity_list = [
            QuantityElement(epc_class=trade_item, quantity=10, uom='EA'),
            QuantityElement(epc_class=trade_item, quantity=94.3,
                            uom='LB')]
        input_quantity_list = [
            QuantityElement(epc_class=trade_item, quantity=100, uom='EA'),
            QuantityElement(epc_class=trade_item, quantity=94.3,
                            uom='LB')]

        te = TransformationEvent(
            now, tzoffset, now, event_id, input_epcs,
            input_quantity_list=input_quantity_list,
            output_epc_list=output_epcs,
            output_quantity_list=output_quantity_list,
            transformation_id=str(uuid.uuid4()),
            biz_step=BusinessSteps.repackaging.value,
            disposition=Disposition.returned.value,
            read_point=read_point,
            biz_location=biz_location,
            business_transaction_list=business_transaction_list,
            source_list=source_list,
            destination_list=destination_list,
            error_declaration=error_declaration,
            ilmd=ilmd)
        return te

    def create_object_event_template(self):
        epcs = self.create_epcs()
        # get the current time and tz
        now, tzoffset = get_current_utc_time_and_offset()
        business_transaction_list = self.create_business_transaction_list()
        biz_location, read_point, source_list = self.create_source_list()
        destination_list = self.create_destination_list()
        ilmd = [
            InstanceLotMasterDataAttribute(
                name=LotLevelAttributeName.itemExpirationDate.value,
                value='2015-12-31'),
            InstanceLotMasterDataAttribute(
                name=ItemLevelAttributeName.lotNumber.value,
                value='DL232')
        ]
        oe = self.create_object_event(biz_location, business_transaction_list,
                                      destination_list, epcs, now, read_point,
                                      source_list, tzoffset,
                                      action=Action.add.value,
                                      ilmd=ilmd)
        oe.clean()
        return oe

    def create_epcs(self, start=1000, end=1002):
        # create a range for the number generation
        # (we can use SerialBox as well)
        nums = range(start, end)
        # generate some URNS
        epcs = gtin_urn_generator('305555', '1', '555555', nums)
        return list(epcs)

    def test_create_illegal_object_event(self):
        # create a range for the number generation
        # (we can use SerialBox as well)
        nums = range(1000, 1002)

        # generate some URNS
        epcs = gtin_urn_generator('305555', '555555', '1', nums)

        # get the current time and tz
        now, tzoffset = get_current_utc_time_and_offset()

        action = Action.observe.value
        ilmd = "<ilmd></ilmd>"

        oe = self.create_object_event(None, None,
                                      None, epcs, '01/dfg/2322', None,
                                      None, tzoffset,
                                      action=Action.observe.value,
                                      ilmd=ilmd)
        self.assertRaises(ValidationError, oe.clean)

        oe = self.create_object_event(None, None,
                                      None, epcs, now, None,
                                      None, tzoffset,
                                      action=Action.observe.value,
                                      ilmd=ilmd)
        self.assertRaises(ValidationError, oe.clean)

    def create_object_event(self, biz_location, business_transaction_list,
                            destination_list, epcs, now, read_point,
                            source_list, tzoffset, action=None, ilmd=None):
        # create the event
        event_id = str(uuid.uuid4())
        error_declaration = self.create_error_declaration()
        oe = ObjectEvent(now, tzoffset,
                         record_time=now,
                         action=action,
                         epc_list=epcs,
                         biz_step=BusinessSteps.commissioning.value,
                         disposition=Disposition.encoded.value,
                         business_transaction_list=business_transaction_list,
                         biz_location=biz_location,
                         read_point=read_point,
                         source_list=source_list,
                         destination_list=destination_list,
                         ilmd=ilmd, error_declaration=error_declaration,
                         event_id=event_id)
        return oe

    def create_business_transaction_list(self):
        business_transaction_list = [
            BusinessTransaction('urn:epcglobal:cbv:bt:0555555555555.DE45_111',
                                BusinessTransactionType.Despatch_Advice),
            BusinessTransaction('urn:epcglobal:cbv:bt:0555555555555.00001',
                                BusinessTransactionType.Bill_Of_Lading)
        ]
        return business_transaction_list

    def create_source_list(self):
        # send in the GLN info
        biz_location = gln13_data_to_sgln_urn(company_prefix='305555',
                                              location_reference='123456')
        read_point = gln13_data_to_sgln_urn(company_prefix='305555',
                                            location_reference='123456',
                                            extension='12')
        # create a source list
        source_list = [
            Source(SourceDestinationTypes.possessing_party.value,
                   biz_location),
            Source(SourceDestinationTypes.location.value, read_point)
        ]
        return biz_location, read_point, source_list

    def create_destination_list(self):
        # create a destination and a destination list
        destination_party = gln13_data_to_sgln_urn(company_prefix='0614141',
                                                   location_reference='00001')
        destination_location = gln13_data_to_sgln_urn(company_prefix='0614141',
                                                      location_reference='00001',
                                                      extension='23')
        destination_list = [
            Destination(SourceDestinationTypes.owning_party.value,
                        destination_party),
            Destination(SourceDestinationTypes.location.value,
                        destination_location)
        ]
        return destination_list


if __name__ == '__main__':
    unittest.main()
