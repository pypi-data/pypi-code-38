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
from EPCPyYes.core.SBDH import sbdh, template_sbdh
from EPCPyYes.core.v1_2 import events as yes_events
from quartet_output.evaluation import EventEvaluation, HeaderEvaluation
from quartet_output.models import EPCISOutputCriteria
from quartet_epcis.parsing.parser import QuartetParser
from quartet_epcis.parsing.business_parser import BusinessEPCISParser


class SimpleOutputParser(QuartetParser):
    """
    Inherits from the `BusinessEPCISParser` which, unlike the `QuartetParser`,
    enforces strict business rules within the confines of parsing EPCIS data.
    For example, items that have been decommissioned and are included
    within a message with throw an exception, aggregation is tracked and
    hierarchies are maintained, etc.  For more on the difference
    between these two fundamental parsers see the `quartet_epcis`
    documentation.
    """

    def __init__(
        self,
        stream,
        epcis_output_criteria: EPCISOutputCriteria,
        event_cache_size: int = 1024,
        recursive_decommission: bool = True
    ):
        super().__init__(stream, event_cache_size, recursive_decommission)
        self.epcis_output_criteria = epcis_output_criteria
        self.event_evaluation = EventEvaluation()
        self.filtered_events = []

    def handle_aggregation_event(
        self,
        epcis_event: yes_events.AggregationEvent
    ):
        """
        Handles any aggregation events as they are found, inserts them into
        the database and then inspects them for output determination.
        :param epcis_event: The event to insert and inspect.
        :return: None
        """
        super().handle_aggregation_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_transaction_event(
        self,
        epcis_event: yes_events.TransactionEvent
    ):
        """
        Handles any transaction events as they are found, inserts them into
        the database and then inspects them for output determination.
        :param epcis_event: The event to insert and inspect.
        :return: None
        """
        super().handle_transaction_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_object_event(self, epcis_event: yes_events.ObjectEvent):
        """
        Handles any object events as they are found, inserts them into
        the database and then inspects them for output determination.
        :param epcis_event: The event to insert and inspect.
        :return: None
        """
        super().handle_object_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_transformation_event(
        self,
        epcis_event: yes_events.TransformationEvent
    ):
        """
        Handles any transformation events as they are found, inserts them into
        the database and then inspects them for output determination.
        If an event is determined to be meeting an outbound criteria
        configuration then it is added to this class's `filtered_events`
        list.
        :param epcis_event: The event to insert and inspect.
        """
        super().handle_transformation_event(epcis_event)
        self.evaluate(epcis_event)

    def evaluate(self, epcis_event):
        if self.event_evaluation.evaluate_event(
            epcis_event,
            self.epcis_output_criteria
        ):
            self.filtered_events.append(epcis_event)


class BusinessOutputParser(BusinessEPCISParser):
    """
    Inherits from the `BusinessEPCISParser` which, unlike the `QuartetParser`,
    enforces strict business rules within the confines of parsing EPCIS data.
    For example, items that have been decommissioned and are included
    within a message with throw an exception, aggregation is tracked and
    hierarchies are maintained, etc.  For more on the difference
    between these two fundamental parsers see the `quartet_epcis`
    documentation.
    """

    def __init__(
        self,
        stream,
        epcis_output_criteria: EPCISOutputCriteria,
        event_cache_size: int = 1024,
        recursive_decommission: bool = True
    ):
        super().__init__(stream, event_cache_size, recursive_decommission)
        self.epcis_output_criteria = epcis_output_criteria
        self.event_evaluation = EventEvaluation()
        self.header_evaluation = HeaderEvaluation()
        self.filtered_events = []

    def handle_aggregation_event(
        self,
        epcis_event: yes_events.AggregationEvent
    ):
        """
        Handles any aggregation events as they are found, inserts them into
        the database and then inspects them for output determination.
        :param epcis_event: The event to insert and inspect.
        :return: None
        """
        super().handle_aggregation_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_transaction_event(
        self,
        epcis_event: yes_events.TransactionEvent
    ):
        """
        Handles any transaction events as they are found, inserts them into
        the database and then inspects them for output determination.
        :param epcis_event: The event to insert and inspect.
        :return: None
        """
        super().handle_transaction_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_object_event(self, epcis_event: yes_events.ObjectEvent):
        """
        Handles any object events as they are found, inserts them into
        the database and then inspects them for output determination.
        :param epcis_event: The event to insert and inspect.
        :return: None
        """
        super().handle_object_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_transformation_event(
        self,
        epcis_event: yes_events.TransformationEvent
    ):
        """
        Handles any transformation events as they are found, inserts them into
        the database and then inspects them for output determination.
        If an event is determined to be meeting an outbound criteria
        configuration then it is added to this class's `filtered_events`
        list.
        :param epcis_event: The event to insert and inspect.
        """
        super().handle_transformation_event(epcis_event)
        self.evaluate(epcis_event)

    def handle_sbdh(self,
                    header: template_sbdh.StandardBusinessDocumentHeader):
        '''
        Hanles any business document headers and checks them for output
        determination.
        :param header:
        :return: True or False if the header values match.
        '''
        super().handle_sbdh(header)
        self.evaluate_header(header)

    def evaluate_header(self, header: sbdh.StandardBusinessDocumentHeader):
        if self.header_evaluation.evaluate_header(
            header,
            self.epcis_output_criteria
        ):
            self.filtered_events.append(header)

    def evaluate(self, epcis_event):
        if self.event_evaluation.evaluate_event(
            epcis_event,
            self.epcis_output_criteria
        ):
            self.filtered_events.append(epcis_event)
