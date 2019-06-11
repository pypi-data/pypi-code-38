"""Server class"""

import re
import cloudpassage.sanity as sanity
from .utility import Utility as utility
from .http_helper import HttpHelper
from .exceptions import CloudPassageResourceExistence
from .halo_endpoint import HaloEndpoint


class Server(HaloEndpoint):
    """Initializing the Server class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.


    Supported keyword args for filtering Server.list_all():
        state (list or str): A list or comma-separated string containing
            any of these: active, missing, deactivated. By default, only active
            servers will be returned.
        platform (list or str): A list or comma-separated string containing
            any of these: `windows`, `debian`, `ubuntu`, `centos`,
            `oracle`, `rhel`.
        cve (str): CVE ID.  Example: CVE-2015-1234
        kb (str): Search for presence of KB.  Example: kb="KB2485376"
        missing_kb (str): Search for absence of KB. Example:
            mising_kb="KB2485376"
    """

    valid_server_states = ["active",
                           "deactivated",
                           "missing"]
    cve_validator = re.compile(r"^CVE-\d+-\d{4,}$")
    kb_validator = re.compile(r"^kb\d+$")
    platform_validator = re.compile(r"^[a-z]+$")
    object_name = "server"
    objects_name = "servers"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def pagination_key(self):
        """Return the pagination key for parsing paged results."""
        return self.objects_name

    def assign_group(self, server_id, group_id):
        """Moves server to another group.

        Args:
            server_id (str): Target server's ID
            group_id (str): ID of group to move server to.

        Returns:
            True if successful, throws exceptions if it fails.

        """

        sanity.validate_object_id(server_id)
        endpoint = "{}/{}".format(self.endpoint(), server_id)
        request_body = {"server": {"group_id": group_id}}
        request = HttpHelper(self.session)
        request.put(endpoint, request_body)
        # Exception will throw if the prior line fails.
        return True

    def delete(self, server_id):
        """Deletes server indicated by server_id.

        Remember, deletion causes the removal of accociated security events and
        scan information.

        Args:
            server_id (str): ID of server to be deleted

        Returns:
            True if successful, throws exceptions otherwise.

        """

        sanity.validate_object_id(server_id)
        endpoint = "{}/{}".format(self.endpoint(), server_id)
        request = HttpHelper(self.session)
        request.delete(endpoint)
        # If no exception from request, we're successful
        return True

    def describe(self, server_id):
        """Get server details by server ID

        Args:
            server_id (str): Server ID

        Returns:
            dict: Dictionary object describing server. Response fields are
                described in detail here:
                https://api-doc.cloudpassage.com/help#servers

        """

        endpoint = "{}/{}".format(self.endpoint(), server_id)
        request = HttpHelper(self.session)
        return request.get(endpoint)["server"]

    def retire(self, server_id):
        """This method retires a server

        Args:
            server_id (str): ID of server to be retired

        Returns:
            True if successful, throws exception on failure

        """

        sanity.validate_object_id(server_id)
        endpoint = "{}/{}".format(self.endpoint(), server_id)
        body = {"server":
                {"retire": True}}
        request = HttpHelper(self.session)
        request.put(endpoint, body)
        # Exceptions fire deeper if this fails.  Otherwise, return True.
        return True

    def issues(self, server_id):
        """This method retrieves the detail of a server issues.

        Args:
            server_id (str): ID of server

        Returns:
            list: issues of the server
        """

        sanity.validate_object_id(server_id)
        endpoint = "{}/{}/issues".format(self.endpoint(), server_id)
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        return response

    def get_firewall_logs(self, server_id, pages):
        """This method retrieves the detail of a server firewall log.

        Args:
            server_id (str): ID of server

        Returns:
            list: firewall log of the server
        """

        sanity.validate_object_id(server_id)
        endpoint = "{}/{}/firewall_logs".format(self.endpoint(), server_id)
        key = "agent_firewall_logs"
        max_pages = pages
        request = HttpHelper(self.session)
        response = request.get_paginated(endpoint, key, max_pages)
        return response

    def command_details(self, server_id, command_id):
        """This method retrieves the details and status of a server command.

        Args:
            server_id (str): ID of server runnung command
            command_id (str): ID of command running on server

        Returns:
            dict: Command status as a dictionary object.

        Example:

        ::

            {
              "name": "",
              "status: "",
              "created_at": "",
              "updated_at": "",
              "result": ""
             }


        For server account creation and server account password resets, \
        the password will be contained in the result field, as a dictionary:


        ::

            {
              "name": "",
              "status: "",
              "created_at": "",
              "updated_at": "",
              "result": {
                         "password": ""
                         }
            }


        """

        endpoint = "{}/{}/commands/{}".format(self.endpoint(), server_id,
                                              command_id)
        request = HttpHelper(self.session)
        return request.get(endpoint)["command"]

    def list_local_accounts(self, server_id):
        """Return all local user accounts associated with `server_id`.

        Args:
            server_id (str): Server ID

        Returns:
            list: List of dictionary objects describing local user account

        """
        endpoint = "{}/{}/accounts".format(self.endpoint(), server_id)
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        local_accounts = response["accounts"]
        return local_accounts

    def describe_local_account(self, server_id, username):
        """Get deatils on local user account

        Args:
            server_id (str): Server ID
            username (str): username of the local user account

        Returns:
            dict: Dictionary object describing local user account

        """
        endpoint = "{}/{}/accounts/{}".format(self.endpoint(), server_id,
                                              username)
        request = HttpHelper(self.session)
        return request.get(endpoint)["account"]

    def list_connections(self, server_id, **kwargs):
        """Return all recent connections detected on `server_id`.

        Args:
            server_id (str): Server ID

        Returns:
            list: List of all recently detected connections on the server

        """
        endpoint = "{}/{}/connections".format(self.endpoint(), server_id)
        params = utility.sanitize_url_params(kwargs)
        request = HttpHelper(self.session)
        response = request.get(endpoint, params=params)
        connections = response["connections"]
        return connections

    def list_processes(self, server_id):
        """This method retrieves information about each running process on a
           specified Linux or Windows server.

        Args:
            server_id (str): Server ID

        Returns:
            list: List of all running processes on the server specified
                  by server ID.

            Note: Historical scan data is not saved;
                  Only the most recent scan results are available
        """

        endpoint = "{}/{}/processes".format(self.endpoint(), server_id)
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        processes = response["processes"]
        return processes

    def list_packages(self, server_id):
        """Return a list of packages installed on the server.

        Args:
            server_id (str): Server ID

        Returns:
            list: List of dictionaries with keys for ``package_name`` and
                ``package_version``. This list will be empty if no SVA scans
                have been completed on the server.
        """

        endpoint = "{}/{}/svm".format(self.endpoint(), server_id)
        request = HttpHelper(self.session)
        packages = []
        try:
            response = request.get(endpoint)
            packages = [{"package_name": x["package_name"],
                         "package_version": x["package_version"]}
                        for x in response["scan"]["findings"]]
        except CloudPassageResourceExistence:  # If there's no scan
            pass
        return packages

    def validate_server_state(self, states):
        """Ensure that server state in query is valid"""
        if isinstance(states, list):
            for state in states:
                if state not in self.valid_server_states:
                    return False
        else:
            if states not in self.valid_server_states:
                return False
        return True

    def validate_platform(self, platforms):
        """Validate platform in query is valid"""
        if isinstance(platforms, list):
            for platform in platforms:
                if not self.platform_validator.match(platform):
                    return False
        else:
            if not self.platform_validator.match(platforms):
                return False
        return True

    def validate_cve_id(self, cve_ids):
        """Validate CVE ID designation"""
        if isinstance(cve_ids, list):
            for cve_id in cve_ids:
                if not self.cve_validator.match(cve_id):
                    return False
        else:
            if not self.cve_validator.match(cve_ids):
                return False
        return True

    def validate_kb_id(self, kb_ids):
        """Validate KB ID is valid"""
        if isinstance(kb_ids, list):
            for kb_id in kb_ids:
                if not self.kb_validator.match(kb_id):
                    return False
        else:
            if not self.kb_validator.match(kb_ids):
                return False
        return True
