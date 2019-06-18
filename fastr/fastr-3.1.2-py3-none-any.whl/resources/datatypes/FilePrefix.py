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

import os

from fastr.data import url
from fastr.datatypes import URLType
from fastr.helpers.checksum import hashsum


class FilePrefix(URLType):
    description = 'Prefix for another file, including the path'
    extension = None  # Explicitly have no extension

    def _validate(value):
        value = value.value

        try:
            if url.isurl(value):
                value = url.get_path_from_url(value)
        except ValueError:
            return False

        return os.path.isdir(os.path.dirname(value))

    def _parse(self):
        return self.value

    def checksum(self):
        return hashsum(self.value)
