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
# Copyright 2019 SerialLab Corp.  All rights reserved
import io
from django.db import transaction
from django.core.files.base import File
from quartet_integrations.divinci.parsing import JSONParser
from quartet_capture.rules import Step, RuleContext


class JSONParsingStep(Step):
    def execute(self, data, rule_context: RuleContext):
        data = self.get_data(data)
        self.info('Parsing inbound data...')
        with transaction.atomic():
            parser = JSONParser(data)
            parser.parse()
        self.info('Parsing complete.')

    def get_data(self, data):
        try:
            if not isinstance(data, File):
                data = io.BytesIO(data).read().decode('utf-8')
        except TypeError:
            try:
                data = io.BytesIO(data.encode())
            except AttributeError:
                self.error('Could not convert the inbound data into an '
                           'expected format for the parser.')
                raise
        return data

    def declared_parameters(self):
        return None

    def on_failure(self):
        pass
