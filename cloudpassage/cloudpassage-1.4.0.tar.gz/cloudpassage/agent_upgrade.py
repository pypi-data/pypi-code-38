"""AgentUpgrade Class"""

from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint


class AgentUpgrade(HaloEndpoint):
    """Initializing the AgentUpgrade class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    """
    object_name = "agent_upgrade"
    objects_name = "agent_upgrades"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def list_all(self):
        """Returns a list of scheduled and started upgrade requests.

        Returns:
            list: List of dictionary object describing upgrade requests.
        """

        endpoint = self.endpoint()
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        return response["upgrades"]

    def status(self, upgrade_id):
        """View the progress of each agent upgrade request.

        You can make this call within 24 hours after an
        upgrade completes to view the completed status.

        Args:
            upgrade_id (str): The ID of the agent upgrade request job.

        Returns:
            dict: Dictionary object describing the status of a
            specific scheduled and started upgrade request.
        """

        endpoint = "/v1/agent_upgrades/%s" % upgrade_id
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        return response

    def create(self, **kwargs):
        """Create a request to upgrade agents

        Keyword Args:
            id (str): Server ID
            group_id (str): Server group ID
            descendants (boolean): Combined child server group or not
            os_type (str): Linux or Windows
            agent_version (str): The version of the installed Halo agent
            agent_version_gte (str): An agent version that is greater than,
                or equal to, the agent version specified
            agent_version_gt (str): An agent version that is greater than
                the agent version specified
            agent_version_lte (str): An agent version that is less than,
                or equal to, the agent version specified
            agent_version_lt (str): An agent version that is less than
                the agent version specified

        Returns:
            string: agent upgrade request ID.
        """

        endpoint = "/v1/agent_upgrades"
        request = HttpHelper(self.session)
        body = {"upgrade": kwargs}
        response = request.post(endpoint, body)
        return response["upgrade"]["id"]

    def delete(self, upgrade_id):
        """Deletes a scheduled upgrade job that you specify by ID.

        If the call is successful, the scheduled upgrade request is
        canceled and no action is taken on any of the agents within that job.

        Args:
            upgrade_id (str):The ID of the agent upgrade request job.

        Returns:
            None if successful, exceptions otherwise.
        """

        endpoint = "/v1/agent_upgrades/%s" % upgrade_id
        request = HttpHelper(self.session)
        request.delete(endpoint)
        return None
