"""LocalUserGroup Class"""

from .utility import Utility as utility
from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint


class LocalUserGroup(HaloEndpoint):
    """Initializing the LocalUserGroup class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.
    """

    object_name = "local_group"
    objects_name = "local_groups"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def list_all(self, **kwargs):
        """Return a list of all local user groups.

        This will only return a maximum of 50 pages, which amounts
        to 500 local user groups.

        Keyword Args:
            group_id (list or str): A list of local user groups in the
                according server group
            server_id (list or str): A list of local user groups in the
                according server
            os_type (list or str): A list of local user groups in the according
                os type
            name (list or str): A list of local user groups with the according
                name
            memebers (list or str): A list of local user groups with the
                according members
            comment (str):  A list of local user groups with the according
                comment
            member_name (list or str): A list of local user groups with the
                according member names
            server_name (list or str): A list of local user groups with the
                according server name
            server_label (list or str): A list of local user groups with the
                according server label
            gid (list or str): A list of local user groups with the according
                gid
            sid (list or str): A list of local user groups with the according
                sid

        Returns:
            list: List of dictionary objects describing local user groups

        """
        endpoint = self.endpoint()
        max_pages = 50
        request = HttpHelper(self.session)
        params = utility.sanitize_url_params(kwargs)
        response = request.get_paginated(endpoint, self.objects_name,
                                         max_pages, params=params)
        return response

    def describe(self, server_id, gid):
        """Get local user group deatils by server id and gid

        Args:
            server_id (str): ID of server to retrieve group information for.
            gid (str): ID of group to query, for server with `server_id`

        Returns:
            list: List of dictionary object describing local user group detail

        """
        endpoint = self.endpoint()
        params = {"server_id": server_id, "gid": gid}
        request = HttpHelper(self.session)
        response = request.get(endpoint, params=params)
        group_detail = response[self.objects_name]
        return group_detail
