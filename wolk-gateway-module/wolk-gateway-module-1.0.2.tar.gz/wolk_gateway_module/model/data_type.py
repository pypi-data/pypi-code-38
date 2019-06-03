"""Data types for creating generic reading types.

Used to visualise data on WolkAbout IoT Platform.
"""
#   Copyright 2019 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from enum import Enum, unique


@unique
class DataType(Enum):
    """Use to create a generic reading type.

    :ivar BOOLEAN: Generic boolean reading type
    :vartype BOOLEAN: int
    :ivar NUMERIC: Generic numeric reading type
    :vartype NUMERIC: int
    :ivar STRING: Generic string reading type
    :vartype STRING: int
    """

    NUMERIC = 0
    BOOLEAN = 1
    STRING = 2
