"""Reading type used for registering devices on WolkAbout IoT Platform."""
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

from typing import Optional, Union

from wolk_gateway_module.model.data_type import DataType
from wolk_gateway_module.model.reading_type_measurement_unit import (
    ReadingTypeMeasurementUnit as Unit,
)
from wolk_gateway_module.model.reading_type_name import ReadingTypeName as Name


class ReadingType:
    """
    Reading type used for registering sensors on WolkAbout IoT Platform.

    Define a reading type for sensors,
    either a generic type by specifying
    a ``DataType`` (numeric, boolean or string) or entering
    a predefined one by using the enumerations provided in
    ``ReadingTypeName`` and ``ReadingTypeMeasurementUnit`` .

    Custom reading types can be used by passing string values
    for the name and measurement unit.

    :ivar name: Name of reading type
    :vartype name: Union[ReadingTypeName, str]
    :ivar unit: Measurement unit of reading type
    :vartype unit: Union[ReadingTypeMeasurementUnit, str]
    """

    def __init__(
        self,
        data_type: Optional[DataType] = None,
        name: Optional[Union[Name, str]] = None,
        unit: Optional[Union[Unit, str]] = None,
    ):
        """Reading type used for registering device's sensors.

        :param data_type: Data type for generic reading type
        :type data_type: Optional[DataType]
        :param name: Reading type name from defined enumeration or string for custom
        :type name: Optional[Union[ReadingTypeName, str]]
        :param unit: Reading type measurement unit from defined enumeration or string for custom
        :type unit: Optional[Union[ReadingTypeMeasurementUnit, str]]

        :raises ValueError: Unable to create a reading type from given input
        """
        if not data_type and not name and not unit:
            raise ValueError("Nothing passed, can't create reading type")

        if data_type:
            if not isinstance(data_type, DataType):
                raise ValueError("Invalid data type given")
            if data_type == DataType.NUMERIC:
                self.name = Name.GENERIC
                self.unit = Unit.NUMERIC
            elif data_type == DataType.BOOLEAN:
                self.name = Name.GENERIC_BOOLEAN
                self.unit = Unit.BOOLEAN
            elif data_type == DataType.STRING:
                self.name = Name.GENERIC_TEXT
                self.unit = Unit.TEXT
            return

        if not (name and (isinstance(unit, str) or isinstance(unit, Unit))):
            raise ValueError("Both name and unit must be provided")

        if not ReadingType.validate(name, unit):
            raise ValueError("Invalid reading type name or unit")

        self.name = name
        self.unit = unit

    def __repr__(self) -> str:
        """Make string representation of reading type.

        :returns: representation
        :rtype: str
        """
        return f"ReadingType(name='{self.name}', unit='{self.unit}')"

    @staticmethod
    def validate(name: Union[Name, str], unit: Union[Unit, str]) -> bool:
        """Validate reading type name and measurement unit.

        :param name: Reading type name
        :type name: Union[ReadingTypeName, str]
        :param unit: Reading type measurement unit
        :type unit: Union[ReadingTypeMeasurementUnit, str]

        :returns: valid
        :rtype: bool
        """
        if not (isinstance(name, Name) or type(name) == str):
            return False
        if not (isinstance(unit, Unit) or type(unit) == str):
            return False

        if type(name) == str and type(unit) == str:
            return True

        if name == Name.GENERIC:
            return (
                True
                if unit == Unit.NUMERIC
                or unit == Unit.BIT
                or unit == Unit.PERCENT
                or unit == Unit.CO2_MOL
                or unit == Unit.X10C
                or unit == Unit.X100V
                or unit == Unit.X10PA
                else False
            )
        elif name == Name.TEMPERATURE:
            return (
                True
                if unit == Unit.KELVIN
                or unit == Unit.CELSIUS
                or unit == Unit.FAHRENHEIT
                or unit == Unit.CELSIUS_X2
                or unit == Unit.CELSIUS_X10
                else False
            )
        elif name == Name.PRESSURE:
            return (
                True
                if unit == Unit.PASCAL
                or unit == Unit.MILLIMETER_OF_MERCURY
                or unit == Unit.INCH_OF_MERCURY
                or unit == Unit.BAR
                or unit == Unit.ATMOSPHERE
                or unit == Unit.MILLIBAR
                or unit == Unit.PRESSURE_PERCENT
                or unit == Unit.MILLIBAR_X10
                or unit == Unit.MICROBAR
                or unit == Unit.KILO_PASCAL
                else False
            )
        elif name == Name.HUMIDITY:
            return (
                True
                if unit == Unit.HUMIDITY_PERCENT
                or unit == Unit.HUMIDITY_PERCENT_X10
                else False
            )
        elif name == Name.BATTERY_VOLTAGE:
            return (
                True
                if unit == Unit.VOLT
                or unit == Unit.MILLIVOLT
                or unit == Unit.CENTIVOLT
                else False
            )
        elif name == Name.MOVEMENT:
            return True if unit == Unit.MOVEMENT else False
        elif name == Name.LIGHT:
            return True if unit == Unit.LIGHT_PERCENT else False
        elif name == Name.ACCELEROMETER:
            return (
                True
                if unit == Unit.METRES_PER_SQUARE_SECOND
                or unit == Unit.GRAVITY
                else False
            )
        elif name == Name.GYROSCOPE:
            return True if unit == Unit.GYROSCOPE else False
        elif name == Name.LOCATION:
            return True if unit == Unit.LOCATION else False
        elif name == Name.HEART_RATE:
            return True if unit == Unit.BEATS_PER_MINUTE else False
        elif name == Name.BATTERY_POWER:
            return (
                True
                if unit == Unit.BATTERY or unit == Unit.BATTERY_X1000
                else False
            )
        elif name == Name.BREATHING_RATE:
            return True if unit == Unit.BREATHS_PER_MINUTE else False
        elif name == Name.CALORIES:
            return True if unit == Unit.CALORIES else False
        elif name == Name.ELECTRIC_CURRENT:
            return (
                True
                if unit == Unit.AMPERE or unit == Unit.MILLIAMPERE
                else False
            )
        elif name == Name.POWER:
            return (
                True
                if unit == Unit.WATT
                or unit == Unit.HORSEPOWER
                or unit == Unit.MILLIWATT
                else False
            )
        elif name == Name.FLOOR_POSITION:
            return True if unit == Unit.METER else False
        elif name == Name.FLUID_VOLUME:
            return (
                True
                if unit == Unit.OUNCE_LIQUID_UK
                or unit == Unit.OUNCE_LIQUID_US
                or unit == Unit.LITRE
                or unit == Unit.MILLILITRE
                or unit == Unit.GALLON_UK
                or unit == Unit.GALLON_DRY_US
                else False
            )
        elif name == Name.LENGHT:
            return (
                True
                if unit == Unit.METRE
                or unit == Unit.MILE
                or unit == Unit.FOOT
                or unit == Unit.POINT
                or unit == Unit.INCH
                or unit == Unit.PARSEC
                or unit == Unit.YARD
                or unit == Unit.MILLIMETER
                or unit == Unit.CENTIMETER
                or unit == Unit.KILOMETER
                else False
            )
        elif name == Name.MASS:
            return (
                True
                if unit == Unit.KILOGRAM
                or unit == Unit.GRAM
                or unit == Unit.MILLIGRAM
                or unit == Unit.METRIC_TON
                or unit == Unit.ATOMIC_MASS
                or unit == Unit.GALLON_LIQUID_US
                or unit == Unit.TON_UK
                or unit == Unit.TON_US
                or unit == Unit.POUND
                or unit == Unit.OUNCE
                or unit == Unit.ELECTRON_MASS
                else False
            )
        elif name == Name.SOUND_LEVEL:
            return True if unit == Unit.DECIBEL else False
        elif name == Name.SPEED:
            return (
                True
                if unit == Unit.KNOT
                or unit == Unit.KILOMETERS_PER_HOUR
                or unit == Unit.MILES_PER_HOUR
                or unit == Unit.MACH
                or unit == Unit.SPEED_OF_LIGHT
                or unit == Unit.METER_PER_SECOND
                else False
            )
        elif name == Name.TIME:
            return (
                True
                if unit == Unit.SECOND
                or unit == Unit.MINUTE
                or unit == Unit.HOUR
                or unit == Unit.MONTH
                or unit == Unit.DAY
                or unit == Unit.WEEK
                or unit == Unit.YEAR
                else False
            )
        elif name == Name.MAGNETIC_FLUX_DENSITY:
            return (
                True
                if unit == Unit.TESLA
                or unit == Unit.GAUSS
                or unit == Unit.MICRO_TESLA
                else False
            )
        elif name == Name.RADIATION:
            return (
                True
                if unit == Unit.SIEVERT
                or unit == Unit.BECQUEREL
                or unit == Unit.RUTHERFORD
                or unit == Unit.ROENTGEN
                or unit == Unit.RADIATION_DOSE_EFFECTIVE
                or unit == Unit.CURIE
                else False
            )
        elif name == Name.FORCE:
            return (
                True
                if unit == Unit.NEWTON
                or unit == Unit.POUND_FORCE
                or unit == Unit.GRAVITY_FORCE
                or unit == Unit.KILOGRAM_FORCE
                or unit == Unit.DYNE
                else False
            )
        elif name == Name.MEASURE:
            return (
                True
                if unit == Unit.SQUARE_METRE
                or unit == Unit.CUBIC_METRE
                or unit == Unit.BYTE
                or unit == Unit.GRADE
                or unit == Unit.HECTARE
                or unit == Unit.CUBIC_INCH
                or unit == Unit.REVOLUTION
                or unit == Unit.CENTIRADIAN
                or unit == Unit.RAD
                or unit == Unit.COMPUTER_POINT
                or unit == Unit.DEGREE_ANGLE
                or unit == Unit.SECOND_ANGLE
                or unit == Unit.MINUTE_ANGLE
                or unit == Unit.SPHERE
                or unit == Unit.ARE
                else False
            )
        elif name == Name.ANGLE:
            return True if unit == Unit.RADIAN else False

        elif name == Name.FREQUENCY:
            return (
                True
                if unit == Unit.HERTZ
                or unit == Unit.MEGA_HERTZ
                or unit == Unit.GIGA_HERTZ
                else False
            )
        elif name == Name.MAGNETIC_FLUX:
            return (
                True if unit == Unit.WEBER or unit == Unit.MAXWELL else False
            )
        elif name == Name.ELECTRIC_CAPACITY:
            return (
                True if unit == Unit.FARAD or unit == Unit.FARADAY else False
            )
        elif name == Name.ELECTRIC_RESISTANCE:
            return True if unit == Unit.OHM else False
        elif name == Name.ELECTRIC_MAGNETISM:
            return True if unit == Unit.GILBERT else False
        elif name == Name.ELECTRIC_ENERGY:
            return (
                True
                if unit == Unit.JOULE or unit == Unit.ELECTRON_VOLT
                else False
            )
        elif name == Name.ELECTRIC_INDUCTANCE:
            return True if unit == Unit.HENRY else False
        elif name == Name.ELECTRIC_CONDUCTANCE:
            return True if unit == Unit.SIEMENS else False
        elif name == Name.LUMINOUS_FLUX:
            return True if unit == Unit.LUMEN else False
        elif name == Name.LUMINOUS_INTENSITY:
            return True if unit == Unit.CANDELA else False
        elif name == Name.ILLUMINANCE:
            return True if unit == Unit.LUX else False
        elif name == Name.GENERIC_TEXT:
            return True if unit == Unit.TEXT else False
        elif name == Name.GENERIC_BOOLEAN:
            return True if unit == Unit.BOOLEAN else False

        assert False
