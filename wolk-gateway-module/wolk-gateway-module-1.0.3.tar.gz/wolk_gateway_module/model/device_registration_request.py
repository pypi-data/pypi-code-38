"""Device registration request model."""
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

from wolk_gateway_module.model.device_template import DeviceTemplate


@dataclass
class DeviceRegistrationRequest:
    """Request for device registration.

    :ivar name: Device name
    :vartype name: str
    :ivar key: Unique device key
    :vartype key: str
    :ivar template: Device template
    :vartype template: DeviceTemplate
    :ivar default_binding: Create semantic group for device on Platform
    :vartype default_binding: bool
    """

    name: str
    key: str
    template: DeviceTemplate = field(default_factory=DeviceTemplate)
    default_binding: bool = field(default=True)
