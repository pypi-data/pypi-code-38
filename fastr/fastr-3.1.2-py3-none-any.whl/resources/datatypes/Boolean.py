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
from fastr.datatypes import ValueType


class Boolean(ValueType):
    """
    Datatype representing a boolean
    """

    description = 'A boolean value (True of False)'

    def __str__(self):
        if self._value is None:
            return ''

        # Format the value properly
        if self.format == 'flag' or self.format is None:
            return {True: '__FASTR_FLAG__TRUE___', False: '__FASTR_FLAG__FALSE__'}[self._value]
        elif self.format == 'yn':
            return {True: 'y', False: 'n'}[self._value]
        elif self.format == 'yes':
            return {True: 'yes', False: 'no'}[self._value]
        elif self.format == 'Yes':
            return {True: 'Yes', False: 'No'}[self._value]
        elif self.format == 'YES':
            return {True: 'YES', False: 'NO'}[self._value]
        elif self.format == 'numeric':
            return {True: '1', False: '0'}[self._value]
        elif self.format == 'string':
            return {True: 'true', False: 'false'}[self._value]
        elif self.format == 'String':
            return {True: 'True', False: 'False'}[self._value]
        elif self.format == 'STRING':
            return {True: 'TRUE', False: 'FALSE'}[self._value]
        elif self.format.startswith('CONST:'):
            if self._value:
                return self.format[6:]
            else:
                return '__FASTR_FLAG__FALSE__'
        elif '|' in self.format:
            options = self.format.split('|', 1)  # In the form of "true|false"
            options = {True: options[0], False: options[1]}
            return options[self._value]
        else:
            fastr.log.warning('Unknown Boolean format ({}), reverting to flag'.format(self.format))
            return {True: '__FASTR_FLAG__TRUE___', False: '__FASTR_FLAG__FALSE__'}[self._value]

    def _validate(self):
        """
        Validate the value of the DataType.

        :return: flag indicating validity of Boolean
        :rtype: bool
        """
        if self.value is None:
            return False
        elif isinstance(self.value, bool):
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
        translation_table = {0: False, '0': False, 'false': False, '__fastr_flag__false__': False,
                             1: True, '1': True, 'true': True, '__fastr_flag__true___': True}

        if isinstance(value, str):
            value = str(value.lower())

        if isinstance(value, bool):
            self._value = value
        elif value in translation_table:
            self._value = translation_table[value]
        else:
            self._value = None
            fastr.log.debug('Not a valid value for a Boolean ({}), ignoring!'.format(value))


