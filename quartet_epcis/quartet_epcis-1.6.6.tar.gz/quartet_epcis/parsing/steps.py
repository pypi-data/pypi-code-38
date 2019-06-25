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
import io

from enum import Enum
from quartet_capture import models
from quartet_capture.rules import Step as RuleStep
from quartet_capture.rules import RuleContext
from quartet_epcis.parsing.parser import QuartetParser
from quartet_epcis.parsing.business_parser import BusinessEPCISParser
from quartet_epcis.parsing.json import JSONParser
from django.core.files.base import File
from quartet_capture.models import Rule, Step, StepParameter
from django.utils.translation import gettext as _


class ContextKeys(Enum):
    """
    Contains context keys that steps within this module can / will place
    on the rule context during processing.

    EPCIS_MESSAGE_ID_KEY
    --------------------
    This is the message id that identifies all of the events, headers and
    entries that are parsed when the EPCISParsingStep is called.  When
    the EPCIS parser saves entries, headers and event model instances, it
    associates them all with an inbound message id by creating a
    Message model instance and associating all of these other model instance
    with that message.id property. Once the parsing step is complete it
    will place the message id on the context using this key.
    """
    EPCIS_MESSAGE_ID_KEY = 'MESSAGE_ID'


def create_rule():
    '''
    Creates the default rule.  Used in data-migrations.
    :return: None
    '''
    rule = Rule.objects.create(
        name=_('EPCIS'),
        description=_('Will capture and parse all properly formed inbound '
                      'EPCIS messagess.  Loose or strict enforcement can '
                      'be controlled via step parameters.'),
    )
    step = Step.objects.create(
        name=_('Parse XML'),
        description=_('Parse EPCIS data and save to database. To set loose '
                      'enforcement (capture all messages) change the '
                      '"LooseEnforcement" step parameter to have a '
                      'value of True.'),
        step_class='quartet_epcis.parsing.steps.EPCISParsingStep',
        order=1,
        rule=rule
    )
    StepParameter.objects.create(
        step=step,
        name='LooseEnforcement',
        value='False',
        description=_('If set to true, QU4RTET will capture all properly '
                      'formed EPCIS messages regardless of business context.')
    )


class EPCISParsingStep(RuleStep):
    '''
    Calls the EPCIS parser as a rules.Step that can be used in the
    quartet_capture rule engine.  Puts the Message id on the rule context as
    EPCIS_MESSAGE_ID.
    '''

    def __init__(self, db_task: models.Task, **kwargs):
        super().__init__(db_task, **kwargs)
        # check to see which parser to use if loose enforcement, then
        # use the quartet parser which just captures messages without
        # trying to enforce any business rules (good for testing)
        self.loose_enforcement = self.get_boolean_parameter(
            'LooseEnforcement', False)
        self.format = self.get_parameter('Format', 'XML')

    @property
    def declared_parameters(self):
        return {"LooseEnforcement": "Whether or not the parsing step should "
                                    "simply store the events (True) or if it "
                                    "should validate the EPCIS events using "
                                    "business rule processing. (False). "
                                    "Default is False",
                "Format": "JSON or XML.  If set to XML, the LooseEnforcement "
                          "parameter is examined.  If set to JSON, inbound "
                          "data must be in the EPCPyYes JSON format and will "
                          "be subject to strong business rule enforcement."
                }

    def execute(self, data, rule_context: RuleContext):
        self.info('Inbound format is configured for %s.', self.format)
        if self.format.upper() == 'XML':
            parser_type = QuartetParser if self.loose_enforcement else BusinessEPCISParser
        else:
            parser_type = JSONParser
        self.info('Loose Enforcement of busines rules set to %s',
                  self.loose_enforcement)
        self.info('Parsing message %s.dat', rule_context.task_name)
        try:
            if isinstance(data, File):
                parser = parser_type(data)
            else:
                parser = parser_type(io.BytesIO(data))
        except TypeError:
            try:
                parser = parser_type(io.BytesIO(data.encode()))
            except AttributeError:
                self.error("Could not convert the data into a format that "
                           "could be handled.")
                raise
        # add the message id to the context
        message_id = parser.parse()
        self.info('Adding Message ID %s to the context under '
                  'key MESSAGE_ID.', message_id)
        rule_context.context[
            ContextKeys.EPCIS_MESSAGE_ID_KEY.value
        ] = message_id
        self.info('Parsing complete.')

    def on_failure(self):
        pass


