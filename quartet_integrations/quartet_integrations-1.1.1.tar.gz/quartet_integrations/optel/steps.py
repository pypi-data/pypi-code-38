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


class ConsolidationParsingStep(OptelLineParsingStep):
    """
    Uses the consolidation parser to handle any bloated optel messages.
    """

    def _parse(self, data):
        return ConsolidationParser(data).parse(self.replace_timezone)
