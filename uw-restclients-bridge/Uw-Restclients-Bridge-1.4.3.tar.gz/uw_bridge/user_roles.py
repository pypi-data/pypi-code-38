"""
Interacte with Bridge user roles API.
You only need a single UserRoles object in your app.
"""

import logging
import json
from uw_bridge.models import BridgeUserRole
from uw_bridge import get_resource


logger = logging.getLogger(__name__)
URL = "/api/author/roles"


class UserRoles:

    def __init__(self):
        self.roles = []
        self.id_name_map = {}
        self.name_ip_map = {}
        self.get_user_roles()

    def get_user_roles(self):
        resp = get_resource(URL)
        resp_data = json.loads(resp)
        if resp_data.get("roles") is not None:
            for role in resp_data["roles"]:
                if (role.get("is_deprecated") is False or
                        role.get("is_deprecated") is None):
                    cf = BridgeUserRole(role_id=role.get("id"),
                                        name=role.get("name"))
                    self.roles.append(cf)
                    self.id_name_map[cf.role_id] = cf.name
                    self.name_ip_map[cf.name] = cf.role_id

    def get_roles(self):
        """
        return the list of BridgeUserRole objects
        """
        return self.roles

    def get_role_id(self, name):
        """
        :param name: use role name defined in models.BridgeUserRole
        return the role id corresponding to the give role name
        """
        return self.name_ip_map.get(name)

    def get_role_name(self, role_id):
        """
        return the name corresponding to the give role_id
        """
        return self.id_name_map.get(role_id)

    def new_user_role_by_id(self, role_id):
        """
        Return a new BridgeUserRole object
        to be used in a POST (add new), PATCH (update) request
        :param role_name: use role name defined in models.BridgeUserRole
        """
        return BridgeUserRole(role_id=role_id,
                              name=self.get_role_name(role_id))

    def new_user_role_by_name(self, name):
        """
        Return a new BridgeUserRole object
        to be used in a POST (add new), PATCH (update) request
        :param name: use role name defined in models.BridgeUserRole
        """
        return BridgeUserRole(role_id=self.get_role_id(name), name=name)
