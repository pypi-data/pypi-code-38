"""Alarm template used for registering device on WolkAbout IoT Platform."""
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
from typing import Optional, Dict


@dataclass
class AlarmTemplate:
    """Alarm template for registering device on WolkAbout IoT Platform.

    :ivar name: Alarm name
    :vartype name: str
    :ivar reference: Alarm reference
    :vartype reference: str
    :ivar description: Alarm description
    :vartype description: str
    """

    name: str
    reference: str
    description: Optional[str] = field(default="")

    def to_dto(self) -> Dict[str, str]:
        """Create data transfer object used for registration.

        :returns: dto
        :rtype: Dict[str, str]
        """
        return {
            "name": self.name,
            "reference": self.reference,
            "description": self.description if self.description else "",
        }
