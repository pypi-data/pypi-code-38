"""CveDetail Class"""

from .halo_endpoint import HaloEndpoint
from .http_helper import HttpHelper


class CveDetails(HaloEndpoint):
    """Initializing the CveDetail class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.

    """

    objects_name = "cve_details"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def describe(self, cve_id):
        """Describe a CVE with complete information on one Common
           Vulnerability and Exposure (CVE), as defined by the National
           Institute of Standards and Technology (NIST).

        Args:
            cve_id (str): CVE number

        Returns:
            dict: Dictionary object describing the details of the
                  Common Vulnerability and Exposure specified by CVE number.

        """

        request = HttpHelper(self.session)
        describe_endpoint = "%s/%s" % (self.endpoint(), cve_id)
        response = request.get(describe_endpoint)
        return response

    def list_all(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def create(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def delete(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def update(self):
        """Not implemented for this object."""
        raise NotImplementedError
