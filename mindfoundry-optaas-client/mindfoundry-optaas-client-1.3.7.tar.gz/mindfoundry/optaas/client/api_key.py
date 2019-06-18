from enum import Enum
from typing import Dict

from mindfoundry.optaas.client.session import OPTaaSSession
from mindfoundry.optaas.client.utils import _pprint


class UserRole(Enum):
    STANDARD = "standard"  # Can use all non-admin endpoints except API key-related
    ADMIN = "admin"  # Can use all endpoints including admin ones (API key-related)
    READ_ONLY = "read_only"  # Can use only non-admin GET endpoints


class ApiKey:
    """A key that can be used to interact with OPTaaS.

    Attributes:
        json (Dict): The full JSON representation of this key in OPTaaS.
        id (str): The actual API key.
        role (UserRole): The role assigned to this key.
        expired (bool): Whether this key has expired, i.e. can no longer be used.
    """

    def __init__(self, json: Dict, session: OPTaaSSession) -> None:
        self.json = json
        self.id = json['id']  # pylint: disable=invalid-name
        self.role = json['role']
        self.expired = json['expired']
        self._url = json['_links']['self']['href']
        self._session = session

    def set_role(self, role: UserRole) -> None:
        """Modifies the role associated with an API Key by making a PUT request to OPTaaS. Only available to Admin users."""
        self._session.put(self._url, {"role": role.value})
        self.role = role.value
        self.json['role'] = role.value

    def set_expired(self, expired: bool) -> None:
        """Expires or un-expires an API Key by making a PUT request to OPTaaS. Only available to Admin users."""
        self._session.put(self._url, {"expired": expired})
        self.expired = expired
        self.json['expired'] = expired

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __repr__(self):
        return _pprint(self, 'id', 'role', 'expired')
