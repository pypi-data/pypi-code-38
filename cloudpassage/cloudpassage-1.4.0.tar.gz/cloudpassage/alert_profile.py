"""AlertProfile class"""
from .halo_endpoint import HaloEndpoint
from .http_helper import HttpHelper
from .utility import Utility as utility


class AlertProfile(HaloEndpoint):
    """Initializing the AlertProfile class:

    Filtering options for :func:`AlertProfile.list_all()` can be passed in as
    keyword arguments. Valid filters can be found at
    https://api-doc.cloudpassage.com/help#list-alert-profiles.

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.
    """
    object_name = "alert_profile"
    objects_name = "alert_profiles"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    @classmethod
    def object_key(cls):
        """Return the key used to pull the policy from the json document."""
        return AlertProfile.object_name

    @classmethod
    def pagination_key(cls):
        """Return the pagination key for parsing paged results."""
        return AlertProfile.objects_name

    def create(self, policy_body):
        """Create a policy from JSON document.

        Returns the ID of the new policy
        """
        request = HttpHelper(self.session)
        request_body = utility.policy_to_dict(policy_body)
        return request.post(self.endpoint(),
                            request_body)["id"]
