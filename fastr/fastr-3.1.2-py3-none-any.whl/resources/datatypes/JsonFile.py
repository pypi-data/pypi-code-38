# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from fastr.datatypes import URLType
from fastr.helpers.checksum import hashsum


class JsonFile(URLType):
    description = 'json file'
    extension = 'json'

    def _validate(self):
        try:
            with open(self.parsed_value) as fh_in:
                json.load(fh_in)
                return True

        except ValueError:
            return False

    def checksum(self):
        with open(self.parsed_value) as fh_in:
            data = json.load(fh_in)

        return hashsum([data])
