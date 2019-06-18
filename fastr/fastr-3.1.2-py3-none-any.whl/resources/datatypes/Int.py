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

import fastr
from fastr.core.version import Version
from fastr.datatypes import ValueType


class Int(ValueType):
    description = 'an integer value'

    def _validate(self):
        """
        Validate the value of the DataType.

        :return: flag indicating validity of the Int
        :rtype: bool
        """
        if self.value is None:
            return False
        elif isinstance(self.value, int):
            return True
        else:
            return False

    @property
    def value(self):
        """
        The value of object instantiation of this DataType.
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Setter function for value property
        """
        try:
            self._value = int(value)
        except (ValueError, TypeError):
            self._value = None
            fastr.log.debug('Not a valid value for a Int ({}), ignoring!'.format(value))

