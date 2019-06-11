"""SyetemAnnouncement class"""


from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint


class SystemAnnouncement(HaloEndpoint):
    """Initializing the SystemAnnouncement class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.
    """

    module_name = "system_announcements"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.module_name)

    def list_all(self):
        """Return a list of all system announcements."""
        session = self.session
        endpoint = self.endpoint()
        request = HttpHelper(session)
        response = request.get(endpoint)
        announcement_list = response["announcements"]
        return announcement_list

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
