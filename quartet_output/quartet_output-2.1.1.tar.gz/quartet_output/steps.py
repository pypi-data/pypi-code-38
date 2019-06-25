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
from copy import copy
from enum import Enum
from urllib.parse import urlparse

import io
import requests
import time
from django.core.files.base import File
from django.utils.translation import gettext as _

from EPCPyYes.core.v1_2 import events
from EPCPyYes.core.v1_2.events import Action
from EPCPyYes.core.v1_2 import template_events
from EPCPyYes.core.v1_2.CBV import BusinessSteps, Disposition
from quartet_capture import models, rules, errors as capture_errors
from quartet_capture.rules import RuleContext
from quartet_capture.tasks import create_and_queue_task
from quartet_epcis.db_api.queries import EPCISDBProxy, EntryList
from quartet_epcis.models.choices import EventTypeChoicesEnum
from quartet_epcis.parsing.steps import EPCISParsingStep
from quartet_output import errors
from quartet_output.models import EPCISOutputCriteria, EndPoint
from quartet_output.parsing import SimpleOutputParser, BusinessOutputParser
from quartet_output.transport.http import HttpTransportMixin
from quartet_output.transport.sftp import SftpTransportMixin


class ContextKeys(Enum):
    """
    Containes Rule Context keys that the steps in this module utilize.

    FILTERED_EVENTS_KEY
    ------------------
    This is used by the `OutputParsingStep` to place any events that match
    the outbound determination parameters set by it's configured
    *EPCIS Output Criteria* step parameter value.  Subsequent Steps in this
    module will look for events under this key to verify if they should
    process the events.  The `OutputParsingStep` will place any matching events
    in this key as `EPCPyYes.core.v1_2.template_event` instances.

    EPCIS_OUTPUT_CRITERIA_KEY
    -------------------------
    When the OutputParsingStep loads, it will put an instance of the
    configured `EPCISOutputCriteria` model that was loaded as a result of
    inspecting the `EPCIS Output Criteria` step parameter for that step.
    This model instance is utilized (typically) by downstream transport
    steps that require a reference to the endpoint, protocol and authentication
    information that is stored in the output criteria.

    AGGREGATION_EVENTS_KEY
    ---------------------
    This is utilized by the `UnpackHierarchy` step.  Any
    EPCPyYes.core.v1_2.template_event.AggregationEvents that were created
    as a result of the events in the `FILTERED_EVENTS_KEY` will be placed under
    this key.  Subsequent Steps will use this key to find the aggregation
    events for further processing, sending, storing, rendering, etc.

    AGGREGATION_EVENTS_KEY
    ---------------------
    This is utilized by the `EPCPyYesParsingStep` step.  Any
    EPCPyYes.core.v1_2.template_event.ObjectEvents that were created
    as a result of the events in the `FILTERED_EVENTS_KEY` will be placed under
    this key.  Subsequent Steps will use this key to find the aggregation
    events for further processing, sending, storing, rendering, etc.

    CREATED_TASK_NAME_KEY
    ---------------------
    When the `CreateOutputTaskStep` creates a new task for deferred processing
    it will store the value here for other interested steps to obtain if
    necessary.
    """
    FILTERED_EVENTS_KEY = 'FILTERED_EVENTS'
    EPCIS_OUTPUT_CRITERIA_KEY = 'EPCIS_OUTPUT_CRITERIA'
    AGGREGATION_EVENTS_KEY = 'AGGREGATION_EVENTS'
    OBJECT_EVENTS_KEY = 'OBJECT_EVENTS'
    OUTBOUND_EPCIS_MESSAGE_KEY = 'OUTBOUND_EPCIS_MESSAGE'
    CREATED_TASK_NAME_KEY = 'CREATED_TASK_NAME'


class OutputParsingStep(EPCISParsingStep):
    """
    A Step that can invokes the `quartet_output.EPCISOutputCriteria`
    parser.  This parser looks for matches between the Step's configured
    *EPCIS Output Criteria* model and any inbound EPCIS events to determine
    if subsequent outbound rule processing is necessary.

    The `OutputParsingStep` will place any events that match up against
    the configured *EPCIS Output Criteria* into the Rule Context's context
    dictionary under the key 'FILTERED_EVENTS'.  This will be a list of
    EPCPyYes template events.

    In addition, since the output criteria contains transport information and
    authentication information, it will place this on the context
    under the EPCIS_OUTPUT_CRITERIA_KEY for any
    downstream steps that need to access the criteria values to send any
    data that was created as a result of the filter step.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self.declared_parameters['EPCIS Output Criteria'] = (
            'The name value of an EPCIS Output Criteria configuration.'
        )
        self.epc_output_criteria = self.get_output_criteria()

    def get_output_criteria(self):
        self.info('Retrieving the Step\'s EPCIS Output Criteria '
                  'parameter value...')
        output_criteria = self.get_parameter(_('EPCIS Output Criteria'),
                                             raise_exception=True)
        self.info(_('EPCIS Output Critieria is set to %s' % output_criteria))
        try:
            return EPCISOutputCriteria.objects.get(
                name=output_criteria
            )
        except EPCISOutputCriteria.DoesNotExist:
            exc = EPCISOutputCriteria.DoesNotExist(
                _('EPCISOutputCriteria with name %s could not be found in the '
                  'database.') % output_criteria
            )
            raise exc

    def execute(self, data, rule_context: rules.RuleContext):
        """
        Calls the SimpleOutputParser which looks for any matches
        between the output criteria and any inbound events.
        :param data: The data to parse.
        :param rule_context: Any context supplied by the Rule.
        :return: None
        """
        # before we start, make sure we make the output criteria available
        # to any downstream steps that need it in order to send data.
        rule_context.context[
            ContextKeys.EPCIS_OUTPUT_CRITERIA_KEY.value
        ] = self.epc_output_criteria
        # get the parser to use from the parameter value.
        # the loose_enforcement parameter is from the base class
        # `EPCISParsingStep` and determines which parser to use.
        parser_type = self.get_parser_type()
        self.info('Parser Type %s', str(parser_type))
        try:
            if isinstance(data, File):
                parser = parser_type(data,
                                     self.epc_output_criteria)
            else:
                parser = parser_type(io.BytesIO(data),
                                     self.epc_output_criteria)
        except TypeError:
            parser = SimpleOutputParser(io.BytesIO(data.encode()),
                                        self.epc_output_criteria)
        self.info(_('Parsing the document...'))
        parser.parse()
        self.info(_('Parsing complete.  %s matching events were found.') %
                  str(len(parser.filtered_events)))
        rule_context.context[
            ContextKeys.FILTERED_EVENTS_KEY.value] = parser.filtered_events

    def get_parser_type(self):
        """
        Override to provide a different parser type.
        :return: The `type` of parser to use.
        """
        parser_type = SimpleOutputParser if self.loose_enforcement \
            else BusinessOutputParser
        return parser_type


class FilteredEventStepMixin:
    """
    A mixin with some helper functions to deal with common issues.  To use
    this in your own class do the following in your custom step's `execute`
    function:

    .. code-block:: text

        self.rule_context = rule_context

    This will allow the mixin access to the `RuleContext` instance passed to
    every step by the rule engine.
    """

    def get_filtered_events(self, default=[]):
        """
        Will check to see if any prior rules have filtered any events
        for outbound processing.
        :param default: The value to return if no filtered events are found.
        Default is an empty list.
        :return: Will return the events or an empty list.
        """
        return self.rule_context.context.get(
            ContextKeys.FILTERED_EVENTS_KEY.value, default
        )

    def get_epc_list(self, epcis_event: events.EPCISEvent):
        """
        Based on the type of event will return the proper list since
        an object and aggregation event have different names for their
        lists.
        :param epcis_event:
        :return: A list of EPCS.
        """
        if isinstance(epcis_event, events.AggregationEvent):
            ret = epcis_event.child_epcs
        else:
            ret = epcis_event.epc_list
        return ret

    def get_parent_epc(self, epcis_event: events.EPCISEvent,
                       default: str = None):
        '''
        If the inbound event is a transaction or transformation event,
        will return the parent.  Otherwise, default.
        :param epcis_event:
        :return:
        '''
        if isinstance(epcis_event, events.AggregationEvent) or isinstance(
            epcis_event, events.TransformationEvent
        ):
            return epcis_event.parent_id
        else:
            ret = default
        return ret

    def process_events(self, events: list):
        """
        Override to process any of the EPCPyYes events returned by the
        database proxy.
        :param events: The inbound events to process.
        :return: Return a list of events that have been processed.
        """
        return events


class UnpackHierarchyStep(rules.Step, FilteredEventStepMixin):
    """
    Will take the top level items from any events and unpack them into
    aggregation events.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self.db_proxy = EPCISDBProxy()

    def execute(self, data, rule_context: rules.RuleContext):
        """
        Ignores the data and looks in the RuleContext for any events in the
        rule context that have been selected for outbound message processing
        under the key defined in the `FILTERED_EVENTS_KEY`.

        If there are events in the context under that key, this Step will
        then
        :param data: The original inbound message to the Rule.
        :param rule_context: The RuleContext instance passed in by the
        rule engine.
        """
        self.out_events = []
        self.rule_context = rule_context
        self.info('Unpack hierarchy step executing...')
        # look in the context for any events that matched output determination
        # criteria set forth in an `EPCISOutputCriteria` model instance.
        epcis_events = self.get_filtered_events()
        # use the db_proxy to get all the events for this.
        self.info('Found %s events that were filtered.', len(epcis_events))
        epcs = []
        for epcis_event in epcis_events:
            if isinstance(epcis_event, events.AggregationEvent) or \
                isinstance(epcis_event, events.TransformationEvent):
                self.warning(
                    _('Skipping a transformation or aggregation event. '
                      'these events can not trigger an unpack action '
                      'in the UnpackHierarchyStep.  Only Transaction '
                      'and Object events may do so.'))
            else:
                epcs = epcs + self.get_epc_list(epcis_event)
                try:
                    epcs.append(epcis_event.parent_id)
                except AttributeError:
                    pass

        # use the db proxy to get the EPCPyYes aggregation event history back
        agg_events = self.db_proxy.get_aggregation_events_by_epcs(epcs)
        agg_events = self.process_events(agg_events)
        # add the found events to the context for any downstream steps
        rule_context.context[
            ContextKeys.AGGREGATION_EVENTS_KEY.value] = agg_events

    def on_failure(self):
        pass

    @property
    def declared_parameters(self):
        return super().declared_parameters()


class AddCommissioningDataStep(rules.Step, FilteredEventStepMixin):
    """
    This step will look at the rule context FILTERED_EVENTS_KEY for any filterd
    EPCIS events.  If any are found, this step will use those events to create
    the series of ObjectEvents that created the items and any item children
    in the filtered events.
    """

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        self.db_proxy = EPCISDBProxy()

    def execute(self, data, rule_context: RuleContext):
        '''
        Looks for any filtered events and then creates any object events
        associated with the epcs in the filtered event.
        :param data: The rule data (not used by this step)
        :param rule_context: The rule context.
        '''
        # check for filtered events in the rule context
        epcis_events = rule_context.context.get(
            ContextKeys.FILTERED_EVENTS_KEY.value, []
        )
        # set this to use the mixin
        self.rule_context = rule_context
        self.info('%s filtered events have been found. Processing',
                  len(epcis_events))
        all_events = set({})
        for epcis_event in epcis_events:
            all_events = all_events.union(
                self.process_event(epcis_event, rule_context))

        rule_context.context[ContextKeys.OBJECT_EVENTS_KEY.value] = list(
            all_events)
        self.info('Processing complete.')

    def process_event(self, epcis_event: events.EPCISBusinessEvent,
                      rule_context: RuleContext):
        '''
        Handles any filtered EPCPyYes events found in the context, unpacks
        their children and adds them to EPCPyYes object event instances.
        Any EPCPyYes events created by this function are put on the rule
        context under the OBJECT_EVENTS_KEY key.
        :param epcis_event: An EPCPyYes event found on the context that
        was filtered.
        :param rule_context: The rule context to add any created events to.
        :return:
        '''
        epcs = copy(self.get_epc_list(epcis_event))
        parent = self.get_parent_epc(epcis_event)
        if parent: epcs.append(parent)
        # find if there are any top-level entries- this is a much more
        # efficient database query
        tops = self.db_proxy.get_top_entries(epcs,
                                             select_for_update=False)
        # if there were any tops, remove them from the epcs list so we don't
        # double our efforts
        [epcs.remove(top.identifier) for top in tops]
        # now that we have all the tops, get all of the entries that have
        # the defined tops
        all_children = self.db_proxy.get_entries_by_tops(
            tops,
            select_for_update=False
        )
        # now get any entries from any of the other epcs that are parent-level
        # if any
        parents = self.db_proxy.get_parent_entries(
            epcs,
            select_for_update=False
        )
        all_children = all_children | self.handle_parent_entries(parents)
        # now find all the commissioning events for these
        all_events = self.db_proxy.get_events_by_entry_list(
            all_children | parents | tops,
            event_type=EventTypeChoicesEnum.OBJECT.value
        )
        # remove any non-commissioning object events
        all_events = [e for e in all_events if e.action == 'ADD']
        all_events = self.process_events(all_events)
        self.info('Adding %s Object events to the rule context.',
                  len(all_events))
        return set(all_events)

    def handle_parent_entries(self, parent_entries: EntryList):
        '''
        Recursively walks a hierarchy and pulls out epcs for processing.
        :param parent_entries: Entries that represent EPCs that are parent
        EPCs.
        :return: All of the children found for the given entries.
        '''
        # the epcs in the event automatically are assumed to be part of an
        # object event of commissioning so we have them already, now we
        # need to see if there are any "parents" in the child list
        # of the event and add those children as well.
        all_children = self.db_proxy.get_entries_by_parents(parent_entries,
                                                            select_for_update=False)
        for child in all_children:
            if child.is_parent:
                all_children = all_children | self.handle_parent_entries(
                    [child])
        return all_children

    def on_failure(self):
        pass

    @property
    def declared_parameters(self):
        return super().declared_parameters()


class AddEventsByMessageStep(rules.Step, FilteredEventStepMixin):
    """
    This step will look at the rule context FILTERED_EVENTS_KEY for any filtered
    EPCIS events.  If any are found, this step will use those events to create
    look up the message id of each and add all messages that were part of
    that message.  This is typically used to forward on all inbound event data
    after it has been parsed.
    """

    def execute(self, data, rule_context: RuleContext):
        '''
        Looks for any filtered events and then creates any object events
        associated with the epcs in the filtered event.
        :param data: The rule data (not used by this step)
        :param rule_context: The rule context.
        '''
        # check for filtered events in the rule context
        epcis_events = rule_context.context.get(
            ContextKeys.FILTERED_EVENTS_KEY.value, []
        )
        # set this to use the mixin
        self.rule_context = rule_context
        self.info('%s filtered events have been found. Processing',
                  len(epcis_events))
        for epcis_event in epcis_events:
            self.process_event(epcis_event, rule_context)
        self.info('Processing complete.')

    def process_event(self, epcis_event: events.EPCISBusinessEvent,
                      rule_context: RuleContext):
        """
        Processes any filtered events.
        :param epcis_event: A filtered event.
        :param rule_context: The rule context for this step.
        :return: None[
        """
        EPCISDBProxy().get_full_message(

        )


class EPCPyYesOutputStep(rules.Step, FilteredEventStepMixin):
    """
    Will look for any EPCPyYes events in the context and render them to
    XML or JSON depending on the step parameter configuration.
    """

    def execute(self, data, rule_context: RuleContext):
        """
        Pulls the object, agg, transaction and other events out of the context
        for processing.  See the step parameters
        :param data: The original message (not used by this step).
        :param rule_context: The RuleContext containing any filtered events
        and also any EPCPyYes events that were created by prior steps.
        """
        self.rule_context = rule_context
        append_filtered_events = self.get_boolean_parameter(
            'Append Filtered Events', True)
        prepend_filtered_events = self.get_boolean_parameter(
            'Prepend Filtered Events', False
        )
        only_filtered = self.get_boolean_parameter(
            'Only Render Filtered Events', False
        )
        oevents = rule_context.context.get(ContextKeys.OBJECT_EVENTS_KEY.value,
                                           [])
        aggevents = rule_context.context.get(
            ContextKeys.AGGREGATION_EVENTS_KEY.value, [])
        if only_filtered:
            all_events = self.get_filtered_events()
        else:
            if append_filtered_events:
                if prepend_filtered_events:
                    all_events = self.get_filtered_events() + oevents + aggevents
                else:
                    all_events = oevents + aggevents + self.get_filtered_events()
            else:
                all_events = oevents + aggevents
        if len(all_events) > 0:
            epcis_document = self.get_epcis_document_class(all_events)
            if self.get_boolean_parameter('JSON', False):
                data = epcis_document.render_json()
            else:
                data = epcis_document.render()
            rule_context.context[
                ContextKeys.OUTBOUND_EPCIS_MESSAGE_KEY.value
            ] = data

    def get_epcis_document_class(self,
                                 all_events) -> template_events.EPCISEventListDocument:
        """
        Override this to provide the step with an alternate class or to
        override the default template provided.
        :param all_events: The EPCPyYes template events to populate
        the document with.
        :return: By default returns a `template_events.EPCISEventListDocument`
        instance.
        """
        epcis_document = template_events.EPCISEventListDocument(all_events)
        return epcis_document

    def declared_parameters(self):
        return {
            "Append Filtered Events": _('Whether or not to append any events '
                                        'found in the rule context under the '
                                        'FILTERED_EVENTS_KEY to the new '
                                        'message.'),
            "Prepend Filtered Events": _('Whether or not to add the filtered '
                                         'events to the beginning of the '
                                         'message or the end. If this is True,'
                                         ' then all filtered events will be'
                                         'added to the beginning of the EPCIS '
                                         'EventList- otherwise they will be '
                                         'added to the end.'),
            "Only Render Filtered Events": _('If set to True, the step will '
                                             'only render the filtered events. '
                                             'If this is true, Append Filtered '
                                             'Events and Prepend Filtered '
                                             'Events will be ignored.'),
            "JSON": _('If set to True then the output message for the EPCPyYEs'
                      'events will be JSON.'),
        }

    def on_failure(self):
        pass


class CreateOutputTaskStep(rules.Step):
    '''
    Will look for any data in the rule context under the
    OUTBOUND_EPCIS_MESSAGE_KEY context key.  If data is found there,
    this step will create a new task for the rule engine to process with
    the data found in the context as the data to be processed by the rule.
    To configure what Rule this step will create the new task under,
    set the **Output Rule** step parameter value to the name of a rule to
    execute.

    If the `Forward Data` *Step Parameter* is set to True, the step will
    forward the inbound message (not the message data in the context) if
    there are any events in the `rule_context.FILTERED_EVENTS_KEY` list.
    Events in this list would mean that the output evaluation was successful
    and that the **ENTIRE** inbound message should be sent somewhere using
    the *Endpoint* defined in the output criteria.
    '''

    def execute(self, data, rule_context: RuleContext):
        '''
        Checks the context for any data under the OUTBOUND_EPCIS_MESSAGE_KEY
        and then creates a task in the rule engine using the *Outbound Rule*
        step parameter.
        :param data: The data to process.
        :param rule_context: The rule context.
        '''
        # get any filtered events from the context
        filtered_events = rule_context.context.get(
            ContextKeys.FILTERED_EVENTS_KEY.value,
            []
        )
        # see if we are just going to forward the inbound data or not
        forward_data = self.get_boolean_parameter('Forward Data', False) and \
                       len(filtered_events) > 0
        if not forward_data:
            # check the context to see if we have any epcis data to send
            self.info(_('Checking the rule context for any data under the '
                        'OUTBOUND_EPCIS_MESSAGE_KEY context key.'))
            data = rule_context.context.get(
                ContextKeys.OUTBOUND_EPCIS_MESSAGE_KEY.value
            )
        if data:
            self.info(_('Data or a Forward Data parameter '
                        'instruction was found.  '
                        'Checking for the Output Rule '
                        'parameter in the step parameters.'))
            # get the output rule name
            output_rule_name = self.get_parameter(
                'Output Rule',
                raise_exception=True
            )
            self.info(_('Looking for the EPCISOutputCriteria placed on the '
                        'context by the OutputParsingStep.'))
            # get the epcis output critieria to put in the task parameters
            # output steps need access to the auth and endpoint info therein
            epcis_output_criteria = rule_context.get_required_context_variable(
                ContextKeys.EPCIS_OUTPUT_CRITERIA_KEY.value
            )
            # create a task parameter with the name of the
            # epcis_output_criteria.  the function below will associate with
            # the task after it is created.
            task_param = models.TaskParameter(
                name='EPCIS Output Criteria',
                value=epcis_output_criteria,
                description=_('The name of the EPCIS Output Criteria to '
                              'use during task processing.')
            )
            # send the data and the rule name and task type over
            # to the rule engine to create a task to process the message
            # using the rule specified in this step's 'Output Rule' parameter
            # create it in a waiting state until after parameters are supplied
            run_immediately = self.get_boolean_parameter('run-immediately',
                                                         default=False)
            if forward_data:
                self.info(_('The Forward Data parameter was specified. The '
                            'step will send the inbound, unmodifed data to '
                            'the specified Output Rule.'))
            task = create_and_queue_task(
                data, output_rule_name,
                'Output',
                task_parameters=[task_param],
                run_immediately=run_immediately
            )
            rule_context.context[ContextKeys.CREATED_TASK_NAME_KEY] = task.name
            self.info('Created a new output task %s with rule %s',
                      task.name, output_rule_name)

    def declared_parameters(self):
        return {
            "Output Rule": _('The name of the rule that will process the '
                             'EPCIS output data created by this step.'),
            "Forward Data": _('Boolean.  Whether or not to ignore data in the '
                              'OUTBOUND_EPCIS_MESSAGE_KEY and just forward '
                              'the inbound data to the output rule.')
        }

    def on_failure(self):
        pass


class TransportStep(rules.Step, HttpTransportMixin, SftpTransportMixin):
    '''
    Uses the transport information within the `EPCISOutputCriteria` placed
    on the context under the EPCIS_OUTPUT_CRITERIA_KEY to send any data that
    was placed on the context under the OUTBOUND_EPCIS_MESSAGE_KEY.

    A transport rule is typically configured with one transport step and
    the name of that rule would be specified in a different rule as a
    step parameter to the CreateOutputTaskStep above for example.

    Step Parameters:
        'content-type': 'The content-type to add to the header during any '
                        'http posts, puts, etc. Default is application/'
                        'xml.'
        'file-extension': 'The file extension to specify when posting and '
                          'putting data via http. Default is xml.'
        'body-raw': 'Whether or not the data should be sent as raw body '
                    'or file attachment.'
                    'Defaults to True.'
    '''

    def execute(self, data, rule_context: RuleContext):
        # get the task parameters that we rely on
        try:
            self.info(_('Looking for the task parameter with the EPCIS '
                        'Output Name.'))
            param = models.TaskParameter.objects.get(
                task__name=rule_context.task_name,
                name='EPCIS Output Criteria'
            )
            # now see if we can get the output critieria based on the param
            # value
            self.info(_('Found the output param, now looking up the '
                        'EPCIS Output Criteria instance with name %s.'),
                      param.value
                      )
            output_criteria = EPCISOutputCriteria.objects.get(
                name=param.value
            )
            self.info(_('Found output criteria with name %s.'),
                      output_criteria)
            # check the url/urn to see if we support the protocol
            protocol = self._supports_protocol(output_criteria.end_point)
            self.info('Protocol supported.  Sending message to %s.' %
                      output_criteria.end_point.urn)
            self._send_message(data, protocol, rule_context, output_criteria)

        except models.TaskParameter.DoesNotExist:
            raise capture_errors.ExpectedTaskParameterError(
                _('The task parameter with name EPCIS Output Criteria '
                  'could not be found.  This task parameter is required by '
                  'the TransportStep to function correctly.')
            )

    def _send_message(
        self,
        data: str,
        protocol: str,
        rule_context: RuleContext,
        output_criteria: EPCISOutputCriteria
    ):
        '''
        Sends a message using the protocol specified.
        :param protocol: The scheme of the urn in the output_criteria endpoint.
        :param rule_context: The RuleContext contains the data in the
        OUTBOUND_EPCIS_MESSAGE_KEY value from the `ContextKey` class.
        :param output_criteria: The originating output criteria.
        :return: None.
        '''
        content_type = self.get_parameter('content-type', 'application/xml')
        file_extension = self.get_parameter('file-extension', 'xml')
        put_data = self.get_boolean_parameter('put-data')
        body_raw = self.get_boolean_parameter('body-raw', True)
        if protocol.lower() in ['http', 'https']:
            if not put_data:
                resp = self.post_data(
                    data,
                    rule_context,
                    output_criteria,
                    content_type,
                    file_extension,
                    False,
                    body_raw
                )
            else:
                resp = self.put_data(
                    data,
                    rule_context,
                    output_criteria,
                    content_type,
                    file_extension,
                    body_raw
                )
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as error:
                self.error(error.response.text)
                raise
            if resp.text:
                self.info("Response Receive: %s", resp.text)
        elif protocol.lower() == 'sftp':
            self.sftp_put(data,
                          rule_context,
                          output_criteria,
                          content_type,
                          file_extension)

    def _supports_protocol(self, endpoint: EndPoint):
        '''
        Inspects the output settings and determines if this step can support
        the protocol or not. Override this to support another or more
        protocols.
        :param EndPoint: the endpoint to inspect
        :return: Returns the supported scheme if the protocol is supported or
        None.
        '''
        parse_result = urlparse(
            endpoint.urn
        )
        if parse_result.scheme.lower() in ['http', 'https', 'sftp']:
            return parse_result.scheme
        else:
            raise errors.ProtocolNotSupportedError(_(
                'The protocol specified in urn %s is not supported by this '
                'step or module.'
            ), endpoint.urn)

    def on_failure(self):
        super().on_failure()

    @property
    def declared_parameters(self):
        return {
            'content-type': 'The content-type to add to the header during any '
                            'http posts, puts, etc. Default is application/'
                            'xml',
            'file-extension': 'The file extension to specify when posting and '
                              'putting data via http. Default is xml',
            'body-raw': 'Whether or not the data should be sent as raw body '
                        'or file attachment.'
                        'Defaults to True.',
        }


class DelayStep(rules.Step):
    """
    Will simply introduce a delay (in seconds) within a rule.  This
    step has a default delay setting of one second but can be configured
    to allow uo to ten seconds of delay via a Timeout Interval step
    parameter.
    """

    def execute(self, data, rule_context: RuleContext):
        self.info('Checking for the Timeout Interval step parameter. '
                  'The default is 1 second.  The parameter value is '
                  'in seconds with a max of 10.')
        timeout_interval = self.get_parameter(
            parameter_name='Timeout Interval', default=0
        )
        # if it comes from the database it will be a string
        timeout_interval = int(timeout_interval)
        self.info(
            'Sleeping the thread for %s seconds...' % timeout_interval)
        if timeout_interval > 0:
            time.sleep(timeout_interval)

    @property
    def declared_parameters(self):
        return {
            'Timeout Interval': 'The amount of time in seconds to pause the '
                                'rule.'
        }

    def on_failure(self):
        pass


class EPCPyYesFilteredEventOutputStep(rules.Step, FilteredEventStepMixin):
    """
    Very similar to the EPCPyYesOutput step except that this step will
    only render the filtered events and place them into the same outbound
    OUTBOUND_EPCIS_MESSAGE_KEY context key for processing by a
    CreateOutputTaskStep later in the rule for example.
    """

    def execute(self, data, rule_context: RuleContext):
        """
        Will pull any filtered events off of the rule context using the
        FILTERED_EVENTS_KEY context key.
        :param data: The data coming into the step from the rule.
        :param rule_context: A reference to the rule context.
        """
        self.rule_context = rule_context
        filtered_events = self.get_filtered_events()
        self.info('Found %s filtered events.' % len(filtered_events))
        if len(filtered_events) >= 0:
            epcis_document = template_events.EPCISEventListDocument(
                filtered_events)
            if self.get_boolean_parameter('JSON', False):
                data = epcis_document.render_json()
            else:
                data = epcis_document.render()
            self.info('Warning: this step is overwriting the Outbound '
                      'EPCIS Message key context key data.  If any data '
                      'was in this key prior to this step and had not '
                      'yet been processed, it will have been overwritten.')
            rule_context.context[
                ContextKeys.OUTBOUND_EPCIS_MESSAGE_KEY.value
            ] = data

    @property
    def declared_parameters(self):
        return {}

    def on_failure(self):
        pass


class AppendCommissioningStep(rules.Step, FilteredEventStepMixin):
    """
    Will take all of the unique epcs found in the filtered events
    and create an EPCPyYes commissioning event for those epcs and append it to
    the RuleContext's OBJECT_EVENTS list.  This is different than the
    `AddCommissioningStep above which will look up all of the commissioning
    events of the epcis in the message along with the children of the epcs
    within the message.  This step does not do any recurssive child lookups
    so it is much more efficient to use if you are intending to just lookup
    the commissioning events for the EPCs in a given message.
    """

    def execute(self, data, rule_context: RuleContext):
        epcs = set({})
        for filtered_event in rule_context.context.get(
            ContextKeys.FILTERED_EVENTS_KEY.value,
            []):
            if isinstance(filtered_event, template_events.AggregationEvent):
                epcs = epcs.union(filtered_event.child_epcs)
                epcs.add(filtered_event.parent_id)
            elif isinstance(filtered_event, template_events.ObjectEvent):
                epcs = epcs.union(filtered_event.epc_list)
            elif isinstance(filtered_event, template_events.TransactionEvent):
                epcs = epcs.union(filtered_event.epc_list)
                epcs.add(filtered_event.parent_id)
            elif isinstance(filtered_event, template_events.TransformationEvent):
                raise self.TransformationEventNotSupported(
                    'Auto commissioning for transformation events is not '
                    'supported.'
                )
            else:
                raise self.EventNotSupported(
                    'An event was passed in that was not supported. '
                    'Only EPCPyYes template events can be processed '
                    'by this step.'
                )

        obj_events = self.get_object_events(list(epcs))
        rule_context.context[
            ContextKeys.OBJECT_EVENTS_KEY.value
        ] = obj_events

    def get_object_events(self, epcs):
        db_proxy = EPCISDBProxy()
        obj_events = db_proxy.get_object_events_by_epcs(epcs)
        return obj_events

    def declared_parameters(self):
        pass

    def on_failure(self):
        pass

    class TransformationEventNotSupported(Exception):
        pass

    class EventNotSupported(Exception):
        pass
