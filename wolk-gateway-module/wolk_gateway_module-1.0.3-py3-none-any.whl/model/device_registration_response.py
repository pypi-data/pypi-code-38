"""Response for device registration request."""
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

from wolk_gateway_module.model.device_registration_response_result import (
    DeviceRegistrationResponseResult,
)


@dataclass
class DeviceRegistrationResponse:
    """Response for device registration request.

    Identified by device key and result,
    with an optional description of the error that occurred.

    :ivar key: Unique device key
    :vartype key: str
    :ivar result: Result of the registration process
    :vartype result: DeviceRegistrationResponseResult
    :ivar description: Description of error that occurred
    :vartype description: str
    """

    key: str
    result: DeviceRegistrationResponseResult
    description: str = field(default="")
