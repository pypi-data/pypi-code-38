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
from django.utils.translation import gettext as _
from django.db.utils import IntegrityError
from quartet_capture import models
from quartet_output.models import EndPoint, EPCISOutputCriteria, \
    AuthenticationInfo


def create_output_filter_rule(rule_name='EPCIS Output Filter',
                              delay_rule=False):
    create_criteria()
    if not models.Rule.objects.filter(name=rule_name).exists():
        rule = models.Rule.objects.create(
            name=rule_name,
            description=_('Will inspect inbound messages for output '
                          'processing.')
        )
        parse_step = models.Step.objects.create(
            name=_('Inspect EPCIS'),
            description=_(
                'Parse and insepect EPCIS events using output criteria.'),
            step_class='quartet_output.steps.OutputParsingStep',
            order=1,
            rule=rule
        )
        models.StepParameter.objects.create(
            name='EPCIS Output Criteria',
            step=parse_step,
            value='Test Transaction Criteria',
            description=_(
                'This is the name of the EPCIS Output Criteria record to use.')

        )
        models.Step.objects.create(
            name=_('Add Commissioning Data'),
            description=_(
                'Adds commissioning events for filtered EPCs and their children.'),
            step_class='quartet_output.steps.AddCommissioningDataStep',
            order=2,
            rule=rule
        )
        models.Step.objects.create(
            name=_('Add Aggregation Data'),
            description=_(
                'Adds aggregation events for included EPCs in any filtered events.'),
            step_class='quartet_output.steps.UnpackHierarchyStep',
            order=3,
            rule=rule
        )
        models.Step.objects.create(
            name=_('Render EPCIS XML'),
            description=_(
                'Pulls any EPCPyYes objects from the context and creates an XML message'),
            step_class='quartet_output.steps.EPCPyYesOutputStep',
            order=4,
            rule=rule
        )
        output_step = models.Step.objects.create(
            name=_('Queue Outbound Message'),
            description=_('Creates a Task for sending any outbound data'),
            step_class='quartet_output.steps.CreateOutputTaskStep',
            order=5,
            rule=rule
        )
        models.StepParameter.objects.create(
            step=output_step,
            name='Output Rule',
            value='Transport Rule'
        )
        if delay_rule == True:
            second_parse_step = models.Step.objects.create(
                name=_('Inspect EPCIS'),
                description='Used to assign an output criteria to the second '
                            'message for forwarding filtered events.',
                step_class='quartet_output.steps.OutputParsingStep',
                order=6,
                rule=rule
            )
            models.StepParameter.objects.create(
                name='EPCIS Output Criteria',
                step=second_parse_step,
                value='Test Transaction Criteria',
                description=_(
                    'This is the name of the EPCIS Output Criteria record to use.')

            )
            render_events = models.Step.objects.create(
                name=_('Render Filtered Events'),
                description=_('Takes any events that were filtered by the '
                              'prior step and renders them to XML for '
                              'sending by the next step.'),
                step_class='quartet_output.steps.EPCPyYesFilteredEventOutputStep',
                order=7,
                rule=rule
            )
            queue_outbound_message = models.Step.objects.create(
                name='Queue Outbound Message',
                description=_('Creates a task and sends it to the delayed '
                              'transport rule or whatever transport rule is '
                              'configured via the Output Rule step parameter.'),
                step_class='quartet_output.steps.CreateOutputTaskStep',
                order=8,
                rule=rule
            )
            output_rule_param = models.StepParameter.objects.create(
                name='Output Rule',
                description=_('The name of the rule to send the context '
                              'data to.'),
                value='Delayed Transport Rule',
                step=queue_outbound_message
            )
            sdstep = create_transport_rule(rule_name='Delayed Transport Rule',
                                           add_delay=delay_rule)
        sdstep = create_transport_rule()
        return rule

def create_transport_rule(rule_name='Transport Rule', add_delay=False):
    try:
        trule = models.Rule.objects.create(
            name=rule_name,
            description=_(
                'An output Rule for any data filtered by EPCIS Output Criteria '
                'rules.')
        )
        if add_delay:
            delay_step = models.Step.objects.create(
                name=_('Wait Three Seconds'),
                description=_(
                    "Wait for three seconds until moving to the next "
                    "step"),
                step_class='quartet_output.steps.DelayStep',
                rule=trule,
                order=1
            )
            delay_step_param = models.StepParameter.objects.create(
                name='Timeout Interval',
                value='3',
                description=_(
                    'The amount of time in seconds to pause the rule.'),
                step=delay_step
            )

        sdstep = models.Step.objects.create(
            name=_('Send Data'),
            description=_(
                'This will send the task message using the source EPCIS Output '
                'Critria EndPoint and Authentication Info.'),
            step_class='quartet_output.steps.TransportStep',
            order=2,
            rule=trule
        )
    except IntegrityError:
        trule = models.Rule.objects.get(name=rule_name)
    return trule


def create_criteria(endpoint_name='Local Echo Server',
                    username=None,
                    criteria_name=None):
    try:
        endpoint = EndPoint.objects.create(
            name=_(endpoint_name),
            urn=_('http://localhost')
        )
    except IntegrityError:
        print('Endpoint already exists.')
        endpoint = EndPoint.objects.get(name=endpoint_name)
    try:
        auth = AuthenticationInfo.objects.create(
            username=_('Test User') or username,
            password=_('Test Password'),
            type='Digest',
            description=_('A test user for the example rule.'))
    except IntegrityError:
        print('Authentication info already exists.')
        auth = AuthenticationInfo.objects.get(username='Test User')
    try:
        output = EPCISOutputCriteria.objects.create(
            name=_('Test Transaction Criteria') or criteria_name,
            action='ADD',
            event_type='Transaction',
            biz_location='urn:epc:id:sgln:305555.123456.0',
            end_point=endpoint,
            authentication_info=auth
        )
    except IntegrityError:
        print('Criteria already exists.')
