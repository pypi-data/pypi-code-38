"""Available reading type names."""
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
class ReadingTypeName(Enum):
    """Enumeration of defined reading type names on WolkAbout IoT Platform."""

    GENERIC = "GENERIC"
    TEMPERATURE = "TEMPERATURE"
    PRESSURE = "PRESSURE"
    HUMIDITY = "HUMIDITY"
    BATTERY_VOLTAGE = "BATTERY_VOLTAGE"
    MOVEMENT = "MOVEMENT"
    LIGHT = "LIGHT"
    ACCELEROMETER = "ACCELEROMETER"
    GYROSCOPE = "GYROSCOPE"
    LOCATION = "LOCATION"
    HEART_RATE = "HEART_RATE"
    COUNT = "COUNT"
    BATTERY_POWER = "BATTERY_POWER"
    BREATHING_RATE = "BREATHING_RATE"
    CALORIES = "CALORIES"
    ELECTRIC_CURRENT = "ELECTRIC_CURRENT"
    POWER = "POWER"
    FLOOR_POSITION = "FLOOR_POSITION"
    FLUID_VOLUME = "FLUID_VOLUME"
    LENGHT = "LENGHT"
    MASS = "MASS"
    SOUND_LEVEL = "SOUND_LEVEL"
    SPEED = "SPEED"
    STRING = "STRING"
    SWITCH = "SWITCH"
    TIME = "TIME"
    MAGNETIC_FLUX_DENSITY = "MAGNETIC_FLUX_DENSITY"
    RADIATION = "RADIATION"
    FORCE = "FORCE"
    MEASURE = "MEASURE"
    ANGLE = "ANGLE"
    FREQUENCY = "FREQUENCY"
    MAGNETIC_FLUX = "MAGNETIC_FLUX"
    ELECTRIC_CAPACITY = "ELECTRIC_CAPACITY"
    ELECTRIC_RESISTANCE = "ELECTRIC_RESISTANCE"
    ELECTRIC_CHARGE = "ELECTRIC_CHARGE"
    ELECTRIC_MAGNETISM = "ELECTRIC_MAGNETISM"
    ELECTRIC_ENERGY = "ELECTRIC_ENERGY"
    ELECTRIC_INDUCTANCE = "ELECTRIC_INDUCTANCE"
    ELECTRIC_CONDUCTANCE = "ELECTRIC_CONDUCTANCE"
    LUMINOUS_FLUX = "LUMINOUS_FLUX"
    LUMINOUS_INTENSITY = "LUMINOUS_INTENSITY"
    ILLUMINANCE = "ILLUMINANCE"
    GENERIC_TEXT = "GENERIC_TEXT"
    GENERIC_BOOLEAN = "GENERIC_BOOLEAN"
