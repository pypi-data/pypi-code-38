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

"""
Module for the management of resource limits of compute resources
"""

import re
from typing import Optional, Union


class ResourceLimit:
    # Fields that are valid resource limits
    __slots__ = ('_cores', '_memory', '_time')

    def __init__(self,
                 cores: Optional[int] = 1,
                 memory: Union[str, int, None] = '2G',
                 time: Union[str, int, None] = None):
        """
        An object describing resource requirements/limits for a node

        :param cores: number of cores
        :param memory: memory specification, can be int with number of megabytes
                       or a string with numbers ending on M, G, T, P for megabytes,
                       gigabytes, terrabytes or petabytes. Note that the number has
                       to be an integer, e.g. 1500M would work, whereas 1.5G would
                       be invalid
        :param time: run time specification, this can be an int with the number of
                     seconds or a string in the HH:MM:SS, MM:SS, or SS format. Where
                     HH, MM, and SS are integers representing the number of hours,
                     minutes and seconds.
        """

        self._cores = cores
        self._memory = self._parse_memory(memory)
        self._time = self._parse_time(time)

    def __eq__(self, other) -> bool:
        """
        Check if two resource limits are equal

        :param other: resource limit to test against
        """
        if not isinstance(other, ResourceLimit):
            return NotImplemented

        return self.cores == other.cores and self.memory == other.memory and self.time == other.time

    def __ne__(self, other) -> bool:
        """
        Check if two resource limits are not equal

        :param other: resource limit to test against
        """
        return not self.__eq__(other)

    def __getstate__(self) -> dict:
        return {
            "cores": self._cores,
            "memory": self._memory,
            "time": self._time,
        }

    def __setstate__(self, state: dict):
        self._cores = state.get('cores')
        self._memory = state.get('memory')
        self._time = state.get('time')

    @property
    def cores(self) -> int:
        """
        The required number of gpus
        """
        return self._cores

    @cores.setter
    def cores(self, value: Optional[int]):
        self._cores = value

    @property
    def memory(self) -> int:
        """
        The required memory in megabytes
        """
        return self._memory if self._memory else None

    @memory.setter
    def memory(self, value: Union[str, int, None]):
        self._memory = self._parse_memory(value) if value else None

    @staticmethod
    def _parse_memory(value):
        if value is None:
            return None
        elif isinstance(value, int):
            return value
        elif isinstance(value, str):
            match = re.match(r'^(\d+)\s*([mMgGtTpP])[Bb]?$', value)
            if match:
                number, unit = match.groups()

                # Parse number and unit
                number = int(number)
                unit = {
                    'm': 1,
                    'g': 1024,
                    't': 1024**2,
                    'p': 1024**3,
                }[unit.lower()]

                return number * unit
            else:
                raise ValueError('A memory limit string should be formatted correctly!')
        else:
            raise TypeError('Invalid type of memory limit!')

    @property
    def time(self) -> int:
        """
        The required time in seconds
        """
        return self._time if self._time else None

    @time.setter
    def time(self, value: Union[str, int, None]):
        self._time = self._parse_time(value) if value else None

    @staticmethod
    def _parse_time(value):
        if value is None:
            return None
        elif isinstance(value, int):
            return value
        elif isinstance(value, str):
            match = re.match(r'^(?:(?:(\d+):)?(\d+):)?(\d+)$', value)
            if match:
                hours, minutes, seconds = [int(x) if x else 0 for x in match.groups()]

                return hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError('A time limit string should be formatted correctly!')
        else:
            raise TypeError('Invalid type of time limit!')

    def copy(self) -> 'ResourceLimit':
        """
        Return a copy of current resource limit object
        """
        value = ResourceLimit()
        value.__setstate__(self.__getstate__())
        return value
