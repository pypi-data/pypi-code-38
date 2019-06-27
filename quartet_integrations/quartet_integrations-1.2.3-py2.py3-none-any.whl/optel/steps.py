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
import io

from quartet_capture import models
from quartet_integrations.sap.steps import SAPParsingStep
from quartet_integrations.optel.parsing import OptelEPCISLegacyParser, \
    ConsolidationParser
from quartet_integrations.optel.epcpyyes import get_default_environment
from quartet_output import steps
from gs123.conversion import URNConverter


class AddCommissioningDataStep(steps.AddCommissioningDataStep):
    def process_events(self, events: list):
        """
        Changes the default template and environment for the EPCPyYes
        object events.
        """
        env = get_default_environment()
        for event in events:
            for epc in event.epc_list:
                if ':sscc:' in epc:
                    parsed_sscc = URNConverter(epc)
                    event.company_prefix = parsed_sscc._company_prefix
                    event.extension_digit = parsed_sscc._extension_digit
                    break
            event.template = env.get_template(
                'optel/object_event.xml')
            event._env = env

        return events


class AppendCommissioningStep(steps.AppendCommissioningStep):
    """
    Overrides the defautl AppendCommissioningDataStep to provide object
    events that use the optel template for object events.  This template
    uses the optel linemaster format from the 2013/14 time frame.
    """

    def get_object_events(self, epcs):
        env = get_default_environment()
        object_events = super().get_object_events(epcs)
        for object_event in object_events:
            object_event.template = env.get_template(
                'optel/object_event.xml'
            )
            object_event._env = env
        return object_events


class OptelLineParsingStep(SAPParsingStep):
    """
    A QU4RTET parsing step that can parse SAP XML data that contains
    custom event data.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self.replace_timezone = self.get_boolean_parameter('Replace Timezone',
                                                           False)

    def _parse(self, data):
        return OptelEPCISLegacyParser(data).parse(
            replace_timezone=self.replace_timezone
        )

    @property
    def declared_parameters(self):
        params = super().declared_parameters()
        params['Replace Timezone'] = 'Whether or not to replace explicit ' \
                                     'timezone declarations in event times ' \
                                     'with the timezone offset in the event.'
        return params


class ConsolidationParsingStep(OptelLineParsingStep):
    """
    Uses the consolidation parser to handle any bloated optel messages.
    """

    def _parse(self, data):
        return ConsolidationParser(data).parse(self.replace_timezone)


class EPCPyYesOutputStep(steps.EPCPyYesOutputStep):
    """
    Overrides the standard output step in order to supply a different
    output template for the header of the generated EPCIS document.
    """

    def get_epcis_document_class(self, all_events):
        """
        Replaces the default document template with the optel one.
        :param all_events: The events that will be rendered to XML.
        :return: The document class with a new template specified.
        """
        document = super().get_epcis_document_class(all_events)
        env = get_default_environment()
        template = env.get_template('optel/epcis_events_document.xml')
        context_search_value = self.get_parameter('Context Search Value', None)
        context_reverse_search = self.get_boolean_parameter('Context Reverse Search',
                                                    False)
        additional_context = self.get_parameter('Additional Context')
        if additional_context or context_search_value:
            additional_context = {'object_ilmd': additional_context,
                                  'search_value': context_search_value,
                                  'reverse_search': context_reverse_search
                                  }
            self.info('Adding additional context : %s', additional_context)
            document.additional_context = additional_context
        document.template = template
        return document


    def declared_parameters(self):
        return {
            'Additional Context': 'Any additional data to insert into the'
                                  ' ilmd area of the message.',
            'Context Search Value': 'The value to look for in a given serial '
                              'number to produce the aditional context '
                              'within a message. Default is None',
            'Context Reverse Search': 'Whether or not to include the ' 
                                      'Additional Context if the search value' 
                                      'is found or whether to include it if'
                                      ' the search value is not found.  Set '
                                      'to True to set additional context '
                                      'when the value is no found. Default '
                                      'is False.'
        }

