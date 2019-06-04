"""Device template used for registering device on WolkAbout IoT Platform."""
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

from dataclasses import dataclass, field
from typing import Dict, List

from wolk_gateway_module.model.actuator_template import ActuatorTemplate
from wolk_gateway_module.model.alarm_template import AlarmTemplate
from wolk_gateway_module.model.configuration_template import (
    ConfigurationTemplate,
)
from wolk_gateway_module.model.sensor_template import SensorTemplate


@dataclass
class DeviceTemplate:
    """Contains information required for registering device on Platform.

    A device template consists of lists of templates (actuator, alarm, sensor, configuration)
    that represent what data the device is expected to send and receive.
    All references of a device must be unique.

    Other than data feed templates, there is a ``supports_firmware_update`` parameter
    that specifies if this device has the capability to perform firmware updates.

    Finally, there are type, connectivity and firmware update parameters that are dictionaries
    that will contain more attributes to group together devices, but are unused at this moment.

    :ivar actuators: List of actuators on device
    :vartype actuators: List[ActuatorTemplate]
    :ivar alarms: List of alarms on device
    :vartype alarms: List[AlarmTemplate]
    :ivar configurations: List of configurations on device
    :vartype configurations: List[ConfigurationTemplate]
    :ivar connectivity_parameters: Device's connectivity parameters
    :vartype connectivity_parameters: Dict[str, Union[str, int, float, bool]]
    :ivar supports_firmware_update: Is firmware update enabled for this device
    :vartype supports_firmware_update: bool
    :ivar sensors: List of sensors on device
    :vartype sensors: List[SensorTemplate]
    :ivar type_parameters: Device's type parameters
    :vartype type_parameters: Dict[str, Union[str, int, float, bool]]
    :ivar firmware_update_parameters: Device's firmware update parameters
    :vartype firmware_update_parameters: Dict[str, Union[str, int, float, bool]]
    """

    actuators: List[ActuatorTemplate] = field(default_factory=list)
    alarms: List[AlarmTemplate] = field(default_factory=list)
    configurations: List[ConfigurationTemplate] = field(default_factory=list)
    sensors: List[SensorTemplate] = field(default_factory=list)
    supports_firmware_update: bool = field(default=False)
    type_parameters: Dict = field(default_factory=dict)
    connectivity_parameters: Dict = field(default_factory=dict)
    firmware_update_parameters: Dict = field(default_factory=dict)
