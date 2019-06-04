"""Everything needed for registering a device on WolkAbout IoT Platform."""
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
from typing import List

from wolk_gateway_module.model.device_template import DeviceTemplate


@dataclass
class Device:
    """Device identified by name and key, as well as its template.

    :ivar name: Device's name
    :vartype name: str
    :ivar key: Device's unique key
    :vartype key: str
    :ivar template: Device template that defines data the device will send and receive.
    :vartype template: DeviceTemplate
    """

    name: str
    key: str
    template: DeviceTemplate = field(default_factory=DeviceTemplate)

    def get_actuator_references(self) -> List[str]:
        """Get list of actuator references for device.

        :returns: actuator_references
        :rtype: List[str]
        """
        actuator_references = [
            actuator.reference for actuator in self.template.actuators
        ]
        return actuator_references

    def has_configurations(self) -> bool:
        """Return if device has configuration options.

        :returns: has_configurations
        :rtype: bool
        """
        return bool(self.template.configurations)

    def supports_firmware_update(self) -> bool:
        """Return if device supports firmware update.

        :returns: supports_firmware_update
        :rtype: bool
        """
        return self.template.supports_firmware_update
