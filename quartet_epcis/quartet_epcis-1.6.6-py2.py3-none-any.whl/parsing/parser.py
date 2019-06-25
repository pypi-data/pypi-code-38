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
import logging
from typing import List
import pytz
from datetime import datetime
from dateutil.parser import parse as parse_date
from eparsecis.eparsecis import FlexibleNSParser
from quartet_epcis.models import events, entries, choices, headers
from quartet_epcis.parsing import errors
from EPCPyYes.core.v1_2 import events as yes_events
from EPCPyYes.core.v1_2 import template_events
from EPCPyYes.core.SBDH import template_sbdh
from django.db import transaction
from django.utils.translation import ugettext as _

logger = logging.getLogger('quartet_epcis')
biz_xact_list = List[yes_events.BusinessTransaction]
ilmd_list = List[yes_events.InstanceLotMasterDataAttribute]
source_list = List[yes_events.Source]
destination_list = List[yes_events.Destination]


class QuartetParser(FlexibleNSParser):
    def __init__(self, stream, event_cache_size: int = 1024):
        '''
        Initializes a new QuartetParser.  Item entries and events will
        be cached in memory until either the event_cache_size or
        entry_cache_size limit is reached- whichever occurs first.

        Be aware that the size of the cached database entries may bump up
        against the size limits of query caches in certain RDBMS systems.

        :param stream: The EPCIS stream to parse.
        :param event_cache_size: defaults to 1024.  The number of events
        to cache in memory before pushing to the back-end datastore.
        '''
        super().__init__(stream)
        self.event_cache = {}
        self.entry_cache = {}
        self.quantity_element_cache = []
        self.error_declaration_cache = []
        self.business_transaction_cache = []
        self.ilmd_cache = []
        self.source_cache = []
        self.destination_cache = []
        self.entry_event_cache = []
        self.event_cache_size = event_cache_size
        self.source_event_cache = []
        self.destination_event_cache = []
        self._message = None

    @transaction.atomic
    def parse(self):
        '''
        Creates the message for use in associating events and then
        executes the base-class parse function.
        :return: returns the message id created by the parsing of tbe
        inbound data.  See the headers.Message model in the models
        package.
        '''
        self._message = headers.Message()
        self._message.save()
        super().parse()
        self.clear_cache()
        return self._message.id

    def handle_sbdh(self,
                    header: template_sbdh.StandardBusinessDocumentHeader):
        db_header = headers.SBDH()
        db_header.message = self._message
        db_sbdh_id = headers.DocumentIdentification()
        logger.debug('Saving the document identification data.')
        db_sbdh_id.document_type = header.document_identification.document_type
        db_sbdh_id.creation_date_and_time = \
            header.document_identification.creation_date_and_time
        db_sbdh_id.multiple_type = header.document_identification.multiple_type
        db_sbdh_id.instance_identifier = \
            header.document_identification.instance_identifier
        db_sbdh_id.type_version = header.document_identification.type_version
        db_sbdh_id.standard = header.document_identification.standard
        db_sbdh_id.save()
        db_header.document_identification = db_sbdh_id
        logger.debug('Document identification is saved, looking for '
                     'partner data')
        db_header.save()
        partner_cache = []
        if header.partners:
            for partner in header.partners:
                db_partner = headers.Partner(
                    partner_type=partner.partner_type,
                    header=db_header
                )
                if partner.partner_id:
                    db_partner.authority = partner.partner_id.authority
                    db_partner.identifier = partner.partner_id.value
                if partner.has_contact_info:
                    db_partner.contact = partner.contact
                    db_partner.email_address = partner.email_address
                    db_partner.fax_number = partner.fax_number
                    db_partner.telephone_number = partner.telephone_number
                    db_partner.contact_type_identifier = \
                        partner.contact_type_identifier
                    partner_cache.append(db_partner)
                logger.debug('Adding partner to the sbdh model instance.')
        [p.save() for p in partner_cache]

    def handle_transaction_event(
        self,
        epcis_event: yes_events.TransactionEvent
    ):
        '''
        Called whenever the parser has completed parsing a TransactionEvent
        within an EPCIS xml structure.

        :param epcis_event: An EPCPyYes TransactionEvent class instance.
        :return: Returns the created Event model instance.
        '''
        logger.debug('Handling a transaction event.')
        db_event = self.get_db_event(epcis_event)
        db_event.type = choices.EventTypeChoicesEnum.TRANSACTION.value
        self.handle_entries(db_event, epcis_event.epc_list, epcis_event)
        if epcis_event.parent_id:
            self.handle_top_level_id(epcis_event.parent_id, db_event)
        self.handle_common_elements(db_event, epcis_event)
        self._append_event_to_cache(db_event)
        if len(self.event_cache) >= self.event_cache_size:
            self.clear_cache()
        return db_event

    def handle_top_level_id(self, top_id, db_event):
        '''
        For both transaction and aggregation events.  Will store the parent
        and or/top level id as an Entry in the entry cache.
        '''
        # check the cache
        entry = self.entry_cache.get(
            top_id,
            None,
        )
        # not in the cache then create and put in the cache
        if not entry:
            entry = entries.Entry.objects.get_or_create(
                identifier=top_id,
                decommissioned=False
            )[0]
            self.entry_cache[entry.identifier] = entry

        entryevent = entries.EntryEvent(entry=entry,
                                        event=db_event,
                                        event_time=db_event.event_time,
                                        event_type=db_event.type,
                                        identifier=top_id,
                                        is_parent=True)
        self.entry_event_cache.append(entryevent)
        logger.debug('Cached Entry for top id %s', top_id)

    def handle_aggregation_event(
        self,
        epcis_event: yes_events.AggregationEvent
    ):
        '''
        Executed when an AggregationEvent xml structure has finished parsing.

        :param epcis_event: An EPCPyYes AggregationEvent instance.
        :return: Returns the created Event model instance.
        '''
        logger.debug('Handling ann aggregation event.')
        db_event = self.get_db_event(epcis_event)
        db_event.type = choices.EventTypeChoicesEnum.AGGREGATION.value
        self.handle_entries(db_event, epcis_event.child_epcs, epcis_event)
        self.handle_common_elements(db_event, epcis_event)
        self.handle_top_level_id(epcis_event.parent_id, db_event)
        self._append_event_to_cache(db_event)
        return db_event

    def handle_object_event(self, epcis_event: yes_events.ObjectEvent):
        '''
        Executed when an ObjectEvent xml structure has finished parsing.
        The EParseCIS library will pass in an EPCPyYes ObjectEvent
        class instance for use.

        :param epcis_event: The EPCPyYes ObjectEvent.
        :return: Returns the created Event model instance.
        '''
        logger.debug('Handling an ObjectEvent...')
        db_event = self.get_db_event(epcis_event)
        db_event.type = choices.EventTypeChoicesEnum.OBJECT.value
        self.handle_entries(db_event, epcis_event.epc_list, epcis_event)
        self.handle_common_elements(db_event, epcis_event)
        self.handle_ilmd(db_event.id, epcis_event.ilmd)
        self._append_event_to_cache(db_event)
        return db_event

    def handle_transformation_event(
        self,
        epcis_event: yes_events.TransformationEvent
    ):
        '''
        Executed when a TransformationEvent xml element has completed parsing
        into a valid EPCPyYes TransformationEvent
        :param epcis_event: The EPCPyYes TransformationEvent
        :return: Returns the created Event model instance.
        '''
        logger.debug('Handling a TransformationEvent...')
        db_event = self.get_db_event(epcis_event)
        db_event.type = choices.EventTypeChoicesEnum.TRANSFORMATION.value
        self.handle_common_elements(db_event, epcis_event)
        self.handle_entries(db_event, epcis_event.input_epc_list, epcis_event)
        self.handle_entries(db_event, epcis_event.output_epc_list, epcis_event,
                            output=True)
        self.handle_ilmd(db_event.id, epcis_event.ilmd)
        self._append_event_to_cache(db_event)
        return db_event

    def handle_common_elements(
        self,
        db_event: events.Event,
        epcis_event: yes_events.EPCISBusinessEvent
    ):
        '''
        Helper function to handle the common elements across the Object,
        Transaction and Aggregation event models.
        :param epcis_event: The Event django database model instance.
        :param db_event: The EPCPyYes EPCISBusinessEvent instance being passed
        to the parser.
        '''
        self.handle_business_transactions(
            db_event.id,
            epcis_event.business_transaction_list
        )
        self.handle_source_list(
            db_event.id,
            epcis_event.source_list
        )
        self.handle_destination_list(
            db_event.id,
            epcis_event.destination_list
        )
        if isinstance(epcis_event, yes_events.TransactionEvent) or \
            isinstance(epcis_event, yes_events.ObjectEvent):
            self.handle_quantity_elements(
                db_event.id,
                epcis_event.quantity_list
            )
        elif isinstance(epcis_event, yes_events.AggregationEvent):
            self.handle_quantity_elements(
                db_event.id,
                epcis_event.child_quantity_list
            )
        elif isinstance(epcis_event, yes_events.TransformationEvent):
            self.handle_quantity_elements(
                db_event.id,
                epcis_event.input_quantity_list
            )
            self.handle_quantity_elements(
                db_event.id,
                epcis_event.output_quantity_list,
                is_output=True
            )

    def get_db_event(self, epcis_event):
        '''
        Creates an Event database model with the common fields and returns.
        :param epcis_event: The EPCPyYes event.
        :return: A new Event model instance.
        '''
        db_event = events.Event()
        if not isinstance(epcis_event, yes_events.TransformationEvent):
            db_event.action = epcis_event.action
        db_event.biz_location = epcis_event.biz_location or None
        db_event.biz_step = epcis_event.biz_step or None
        db_event.disposition = epcis_event.disposition or None
        db_event.read_point = epcis_event.read_point or None
        db_event.event_time = epcis_event.event_time
        db_event.event_timezone_offset = epcis_event.event_timezone_offset \
                                         or None
        db_event.event_id = epcis_event.event_id or None
        db_event.record_time = epcis_event.record_time or None
        db_event.message_id = self._message.id
        if epcis_event.error_declaration:
            self.handle_error_declaration(
                db_event.id,
                epcis_event.error_declaration
            )
        return db_event

    def handle_entries(
        self, db_event: events.Event, epc_list: [],
        epcis_event: yes_events.EPCISEvent,
        output: bool = False
    ):
        '''
        Gets the EPCs from the event and caches them for storage in the
        back-end.  Then creates the EntryEvent intersection entity records
        and appends them for storage as well.
        :param db_event: The unique id of the event
        :param epc_list: A list of epcs to be cached.
        :return:
        '''
        logging.debug('Processing epc list %s', epc_list)
        for epc in epc_list:
            created = False
            entry = self.entry_cache.get(epc)
            if entry and isinstance(epcis_event,
                                    yes_events.ObjectEvent) and \
                epcis_event.action == yes_events.Action.add.value:
                raise errors.CommissioningError(
                    'The epc %s has already been commissioned.', epc
                )
            if entry and entry.last_event_time == None and isinstance(
                epcis_event,
                yes_events.AggregationEvent
            ):
                raise errors.CommissioningError('The epc %s has not been '
                                                'commissioned and therefore '
                                                'cannot be aggregated.' % epc
                                                )
            if not entry:
                entry, created = \
                    entries.Entry.objects.get_or_create(identifier=epc,
                                                        decommissioned=False)
            if not created and isinstance(epcis_event,
                                          yes_events.ObjectEvent) and \
                epcis_event.action == yes_events.Action.add.value:
                raise errors.CommissioningError(
                    'The epc %s has already been commissioned.', epc
                )
            # if an event is out of order but not an observation then throw
            # an out of order exception
            event_time = self.get_event_time(epcis_event)
            if not created and event_time < entry.last_event_time \
                and db_event.action != yes_events.Action.observe.value:
                raise self.EventOrderException(_(
                    'An event was received which was temporally '
                    'out of order.  Event ID: %s' % epcis_event.event_id
                ))
            # set the last event pointers
            entry.last_event = db_event
            entry.last_event_time = event_time
            entry.last_disposition = epcis_event.disposition
            # if this is an aggregation event and is not an observation then
            # mark the last agg event pointer and envent type.
            self._check_for_aggregation(db_event, entry, epcis_event)
            entry.save()
            self.entry_cache[entry.identifier] = entry
            entryevent = entries.EntryEvent(entry=entry,
                                            event_time=epcis_event.event_time,
                                            event_type=db_event.type,
                                            event=db_event,
                                            identifier=epc,
                                            output=output)
            self.entry_event_cache.append(entryevent)

    def get_event_time(self, epcis_event: yes_events.EPCISEvent) -> datetime:
        """
        Override to get a valid event time for a given event if you are
        dealing with non ISO or python date strings.
        :param epcis_event: The event with the event time to convert.
        :return: A datetime representing the EPCIS event event time string.
        """
        event_time = parse_date(epcis_event.event_time)
        return event_time

    def _check_for_aggregation(self, db_event, entry, epcis_event):
        '''
        Looks for any aggregation event that is of type ADD or DELETE and
        marks the entry record with the event time, action and Event model
        foreign key.
        :param db_event: The database Event model.
        :param entry: The new Entry instance.
        :param epcis_event: The EPCPyYes event that is being analyzed.
        :return: None.
        '''
        if db_event.type == choices.EventTypeChoicesEnum.AGGREGATION.value \
            and db_event.action != yes_events.Action.observe.value:
            entry.last_aggregation_event = db_event
            entry.last_aggregation_event_time = epcis_event.event_time
            entry.last_aggregation_event_action = epcis_event.action

    def handle_error_declaration(
        self,
        db_event_id: str,
        error_declaration: yes_events.ErrorDeclaration,
    ):
        '''
        Creates an ErrorDeclaration database model and caches
        it for storage in the backend database.
        :param db_event_id: The unique id of the parent event.
        :param error_declaration: The EPCPyYes ErrorDeclaration instance.
        '''
        if isinstance(error_declaration.corrective_event_ids, list):
            logging.debug('Concatenating the corrective event ids')
            cids = ','.join(error_declaration.corrective_event_ids)
        else:
            cids = str(error_declaration.corrective_event_ids)
        ed = events.ErrorDeclaration(
            event_id=db_event_id,
            reason=error_declaration.reason,
            corrective_event_ids=cids,
        )
        self.error_declaration_cache.append(ed)

    def handle_quantity_elements(
        self,
        db_event_id: str,
        quantity_elements: list,
        is_output: bool = False,
    ):
        '''
        Creates a QuantityElement database model and caches it
        for later bulk insert into the backend database.
        :param db_event_id: The source event.
        :param quantity_element: The EPCPyYes QuantityElement
        '''
        for quantity_element in quantity_elements:
            qe = events.QuantityElement(
                event_id=db_event_id,
                epc_class=quantity_element.epc_class,
                quantity=quantity_element.quantity,
                uom=quantity_element.uom,
                is_output=is_output
            )
            logging.debug('Appending quantity element.')
            self.quantity_element_cache.append(qe)

    def handle_business_transactions(self, db_event_id: str,
                                     business_transaction_list: biz_xact_list):
        '''
        Takes each business transaction in the list and creates
        a BusinessTransaction database model instance and caches it
        for bulk insert into the backend database.
        :param db_event_id: The source event primary key/id.
        :param business_transaction_list: A list of EPCPyYes
        BusinessTransactions
        '''
        for transaction in business_transaction_list:
            bt = events.BusinessTransaction(
                event_id=db_event_id,
                biz_transaction=transaction.biz_transaction,
                type=transaction.type
            )
            logging.debug('Appending biz transaction.')
            self.business_transaction_cache.append(bt)

    def handle_ilmd(self, db_event_id: str,
                    ilmd_data: ilmd_list):
        '''
        Takes the ILMD node and creates InstanceLotMasterData model
        instances to be cached for bulk insert into the database.
        :param db_event_id: The source event primary key value.
        :param ilmd_data: The ilmd section of EPCPyYes event.
        '''
        for ilmd in ilmd_data:
            ie = events.InstanceLotMasterData(
                event_id=db_event_id,
                name=str(ilmd.name),
                value=ilmd.value,
            )
            self.ilmd_cache.append(ie)

    def handle_source_list(self, db_event_id: str,
                           sources: source_list):
        '''
        Creates a source database model instance and caches it
        for storage during bulk insert.
        :param db_event_id: The source event primary key.
        :param sources: A list of EPCPyYes Source instances.
        '''
        for source in sources:
            src = events.Source(
                type=source.type,
                source=source.source,
            )
            source_event = events.SourceEvent(source=src,
                                              event_id=db_event_id)
            logger.debug('Adding source %s %s and the source event '
                         'to the cache',
                         source.type, source.source)
            self.source_event_cache.append(source_event)
            self.source_cache.append(src)

    def handle_destination_list(self, db_event_id: str,
                                destinations: destination_list):
        '''
        Creates a destination database model instance and caches
        it for storage during bulk insert.
        :param db_event_id: The source event's primary key.
        :param destinations: A list of EPCPyYes Destination instances.
        '''
        for destination in destinations:
            dest = events.Destination(
                type=destination.type,
                destination=destination.destination
            )
            destination_event = events.DestinationEvent(
                destination=dest,
                event_id=db_event_id
            )
            logger.debug('Adding destination %s %s and the destination event '
                         'to the cache',
                         destination.type, destination.destination)
            self.destination_event_cache.append(destination_event)
            self.destination_cache.append(dest)

    def clear_cache(self):
        '''
        Calls save on all items in all of the caches.
        '''
        logger.debug('Clear cache has been called with %s and %i '
                     'in the event and entry caches respectively',
                     len(self.event_cache), len(self.entry_cache))
        event_cache = self._get_sorted_event_cache()
        events.Event.objects.bulk_create(event_cache)
        logger.debug('Clearing out %s number of EntryEvents.',
                     len(self.entry_event_cache))
        entries.EntryEvent.objects.bulk_create(self.entry_event_cache)
        logger.debug('Clearing cache of %s number of quantity elements',
                     len(self.quantity_element_cache))
        events.QuantityElement.objects.bulk_create(
            self.quantity_element_cache
        )
        logger.debug('Clearing cache of %s number of error declarations',
                     len(self.error_declaration_cache))
        events.ErrorDeclaration.objects.bulk_create(
            self.error_declaration_cache
        )
        logger.debug(
            'Clearing the biz transaction cache of %s transactions',
            len(self.business_transaction_cache))
        events.BusinessTransaction.objects.bulk_create(
            self.business_transaction_cache
        )
        logger.debug('Clearing the ILMD cache of %s objects',
                     len(self.ilmd_cache))
        events.InstanceLotMasterData.objects.bulk_create(self.ilmd_cache)
        logger.debug('Clearing out the source cache of %s items',
                     len(self.source_cache))
        events.Source.objects.bulk_create(self.source_cache)
        logger.debug('Clearing out the destination cache of %s items',
                     len(self.destination_cache))
        events.Destination.objects.bulk_create(self.destination_cache)
        logger.debug('Clearing out the source event cache.')
        events.SourceEvent.objects.bulk_create(self.source_event_cache)
        logger.debug('Clearing out the destination event cache.')
        events.DestinationEvent.objects.bulk_create(
            self.destination_event_cache
        )
        logger.debug('Clearing out the cache lists.')
        self.event_cache.clear()
        self.entry_cache.clear()
        del self.entry_event_cache[:]
        del self.error_declaration_cache[:]
        del self.quantity_element_cache[:]
        del self.business_transaction_cache[:]
        del self.ilmd_cache[:]
        del self.source_cache[:]
        del self.destination_cache[:]
        del self.source_event_cache[:]
        del self.destination_event_cache[:]

    def _append_event_to_cache(self, db_event):
        """
        The internal event cache is a dictionary with a key that has
        an event time and a list as the value.  All events that share
        that time will be consolidated into the one list under the
        event time key.
        :param db_event: The event to add to the cache.
        :return: None
        """
        # get the list associated with the event time
        event_list = self.event_cache.get(db_event.event_time, [])
        # if there was no list then add a new list to that key
        if len(event_list) == 0:
            self.event_cache[db_event.event_time] = event_list
        # add the event to the existing or new list (by reference)
        event_list.append(db_event)

    def _get_sorted_event_cache(self):
        # get the dates
        dates = list(self.event_cache.keys())
        # sort the dates
        dates = sorted(dates)
        # create the sorted list
        ret = []
        for dt in dates:
            ret += self.event_cache.get(dt)
        return ret

    class EventOrderException(Exception):
        pass


class EPCPyYesParser(FlexibleNSParser):
    """
    Simply collects all parsed data into a collection of aggregation,
    object, transaction, transformation and sbdh EPCPyYes instances
    for use in python.  No database models are utilized and no
    database storage takes place.  Simply a way to convert XML to EPCPyYes
    for use in rules, plain old python or other application contexts.
    """

    def __init__(self, stream,
                 header_namespace='http://www.unece.org/cefact/namespaces'
                                  '/StandardBusinessDocumentHeader'):
        super().__init__(stream, header_namespace)
        self.aggregation_events = []
        self.object_events = []
        self.transformation_events = []
        self.transaction_events = []
        self.sbdh = None

    def handle_aggregation_event(
        self,
        epcis_event: template_events.AggregationEvent
    ):
        logger.info('Adding an aggregation event.')
        self.aggregation_events.append(epcis_event)

    def handle_object_event(self, epcis_event: template_events.ObjectEvent):
        logger.info('Adding an object event.')
        self.object_events.append(epcis_event)

    def handle_transaction_event(
        self,
        epcis_event: template_events.TransactionEvent
    ):
        logger.info('Adding a transaction event.')
        self.transaction_events.append(epcis_event)

    def handle_transformation_event(
        self,
        epcis_event: template_events.TransformationEvent
    ):
        logger.info('Adding a transformation event.')
        self.transformation_events.append(epcis_event)

    def handle_sbdh(self,
                    header: template_sbdh.StandardBusinessDocumentHeader):
        logger.info('Setting the header.')
        self.sbdh = header
