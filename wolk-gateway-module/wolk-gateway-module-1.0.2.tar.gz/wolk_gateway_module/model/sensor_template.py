"""Sensor templates used for registering device on WolkAbout IoT Platform."""
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

from typing import Optional, Union, Dict

from wolk_gateway_module.model.data_type import DataType
from wolk_gateway_module.model.reading_type import ReadingType
from wolk_gateway_module.model.reading_type_measurement_unit import (
    ReadingTypeMeasurementUnit as Unit,
)
from wolk_gateway_module.model.reading_type_name import ReadingTypeName as Name


class SensorTemplate:
    """Sensor template for registering device on Platform.

    :ivar description: Description detailing this sensor
    :vartype description: str or None
    :ivar maximum: Maximum sensor value
    :vartype maximum: int or float or None
    :ivar minimum: Minimum sensor value
    :vartype minimum: int or float or None
    :ivar name: Name of sensor
    :vartype name: str
    :ivar reference: Unique sensor reference
    :vartype reference: str
    :ivar unit: Sensor reading type measurement name and unit
    :vartype unit: ReadingType
    """

    def __init__(
        self,
        name: str,
        reference: str,
        data_type: DataType = None,
        reading_type_name: Name = None,
        unit: Unit = None,
        description: Optional[str] = None,
        minimum: Optional[Union[int, float]] = None,
        maximum: Optional[Union[int, float]] = None,
    ):
        """Sensor template for device registration request.

        Define a reading type for sensors,
        either a generic type by specifying
        a ``DataType`` (numeric, boolean or string) or entering
        a predefined one by using the enumerations provided in
        ``ReadingTypeName`` and ``ReadingTypeMeasurementUnit``.

        Custom reading types that have been previously defined
        on WolkAbout IoT Platform can be used by passing string values
        for ``reading_type_name`` and ``unit``.

        :param name: Sensor name
        :type name: str
        :param reference: Sensor reference
        :type reference: str
        :param data_type: Sensor data type for generic reading type
        :type data_type: Optional[DataType]
        :param reading_type_name: Reading type name from defined enumeration or
         string for custom
        :type reading_type_name: Optional[Union[ReadingTypeName, str]]
        :param unit: Reading type measurement unit from defined enumeration
         or string for custom
        :type unit: Optional[Union[ReadingTypeMeasurementUnit, str]]
        :param description: Description detailing the sensor's specification
        :type description: Optional[str]
        :param minimum: Minimum sensor value
        :type minimum: Optional[Union[int, float]]
        :param maximum: Maximum sensor value
        :type maximum: Optional[Union[int, float]]
        """
        self.name = name
        self.reference = reference
        self.description = description
        self.minimum = minimum
        self.maximum = maximum

        if not (data_type or reading_type_name or unit):
            raise ValueError("Unable to create template")

        if data_type:
            if not isinstance(data_type, DataType):
                raise ValueError("Invalid data type given")
            if data_type == DataType.NUMERIC:
                self.unit = ReadingType(DataType.NUMERIC)
            elif data_type == DataType.BOOLEAN:
                self.unit = ReadingType(DataType.BOOLEAN)
            elif data_type == DataType.STRING:
                self.unit = ReadingType(DataType.STRING)
            return

        if not (
            reading_type_name
            and (isinstance(unit, str) or isinstance(unit, Unit))
        ):
            raise ValueError(
                "Both reading type name and unit must be provided"
            )
        self.unit = ReadingType(name=reading_type_name, unit=unit)

    def __repr__(self) -> str:
        """Make string representation of sensor template.

        :returns: representation
        :rtype: str
        """
        return (
            f"SensorTemplate(name='{self.name}', reference='{self.reference}',"
            f" description='{self.description}', unit='{self.unit}', "
            f"minimum='{self.minimum}', maximum='{self.maximum}')"
        )

    def to_dto(self) -> Dict[str, Union[str, int, float]]:
        """Create data transfer object used for registration.

        :returns: dto
        :rtype: Dict[str, Union[str, int, float]]
        """
        dto = {"name": self.name, "reference": self.reference}

        dto["description"] = self.description if self.description else ""

        dto["unit"] = (
            {
                "readingTypeName": self.unit.name.value,
                "symbol": self.unit.unit.value,
            }
            if (
                isinstance(self.unit.name, Name)
                and isinstance(self.unit.unit, Unit)
            )
            else {"readingTypeName": self.unit.name, "symbol": self.unit.unit}
        )

        if self.minimum is not None and self.maximum is not None:
            dto["minimum"] = self.minimum
            dto["maximum"] = self.maximum

        return dto
