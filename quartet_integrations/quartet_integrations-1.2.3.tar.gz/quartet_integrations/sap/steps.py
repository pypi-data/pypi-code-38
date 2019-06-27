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
from quartet_epcis.parsing.steps import ContextKeys
from django.core.files.base import File
from quartet_capture.rules import Step, RuleContext
from quartet_integrations.sap.parsing import SAPParser


class SAPParsingStep(Step):
    """
    A QU4RTET parsing step that can parse SAP XML data that contains
    custom event data.
    """

    def execute(self, data, rule_context: RuleContext):
        data = self.get_data(data)
        # the base class will return a generic message id for the
        # parsed epcis data
        self.info('Beginning parsing...')
        message_id = self._parse(data)
        self.info('Adding Message ID %s to the context under '
                  'key MESSAGE_ID.', message_id)
        self.info('Parsing complete.')
        # add the message id to the context in case rules downstream
        # need access to the data placed into the database as part
        # of this processing
        rule_context.context[
            ContextKeys.EPCIS_MESSAGE_ID_KEY.value
        ] = message_id

    def _parse(self, data):
        return SAPParser(data).parse()

    def get_data(self, data):
        try:
            if not isinstance(data, File):
                data = io.BytesIO(data)
        except TypeError:
            try:
                data = io.BytesIO(data.encode())
            except AttributeError:
                self.error('Could not convert the inbound data into an '
                           'expected format for the parser.')
                raise
        return data

    def on_failure(self):
        pass

    @property
    def declared_parameters(self):
        pass



