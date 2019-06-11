"""LocalUserAccount Class"""

from .utility import Utility as utility
from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint


class LocalUserAccount(HaloEndpoint):
    """Initializing the LocalUserAccount class:

    Args:
        session (:class:`cloudpassage.HaloSession`) This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    """
    object_name = "local_account"
    objects_name = "local_accounts"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def list_all(self, **kwargs):
        """This method retrieves all local user accounts

        Keyword Args:
            os_type (list or str): A list of local user accounts with the
                according os type.
            username (list or str): A list of local user accounts with the
                according username.
            admin (boolean): A list of local user accounts with the according
                admin.
            active (boolean): A list of local user accounts with the according
                active settings.
            last_login_at (str): A list of local user accounts last login at
                date in iso8601 format such as: 2017-01-01.
            never_logged_in (boolean): A list of local user accounts with never
                logged in.
            password_required (boolean): A list of local user accounts with the
                according password_required settings
            password_expired (boolean): A list of local user accounts with the
                according password_expired settings
            comment:  A list of local user accounrs with the according comment
            group_id (list or str): A list of local user accounts
                with the according group id
            server_id (list or str): A list of local user accounts with the
                according server id
            server_name (list or str): A list of local user accounts with the
                according server name
            server_label (list or str): A list of local user accounts with the
                according server label
            group_name (list or str): A list of local user accounts with the
                according group name
            locked (boolean): A list of local user accounts with the according
                locked settings
            gid (list or str): A list of local user accounts with the according
                gid
            sid (list or str): A list of local user accounts with the according
                sid

        Returns:
            list: List of dictionary objects describing local user accounts

        """
        endpoint = self.endpoint()
        key = "accounts"
        max_pages = 50
        request = HttpHelper(self.session)
        params = utility.sanitize_url_params(kwargs)
        response = request.get_paginated(endpoint, key,
                                         max_pages, params=params)
        return response

    def create(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def delete(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def update(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def describe(self):
        """Not implemented for this object."""
        raise NotImplementedError
