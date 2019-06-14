import os

from spell.api.client import APIClient
from spell.api.exceptions import ClientException
from spell.client.runs import RunsService
from spell.client.hyper import HyperService
from spell.client.workflows import Workflow
from spell.configs.config_handler import ConfigHandler, ConfigException, default_config_dir

BASE_URL = "https://api.spell.run"
API_VERSION = "v1"


class SpellClient(object):
    """A client for interacting with Spell.

    Args:
        token (str): the authentication token to use for communicating with Spell.
        workflow_id (int, optional): the id of the workflow to set as the :py:attr:`active_workflow`

    Attributes:
        active_workflow (:py:class:`~spell.client.workflows.Workflow`): the active workflow for the client.
            All runs created will be created in the associated workflow. If the value is ``None``,
            runs are not created in a workflow.
    """

    def __init__(self, token, base_url=BASE_URL, version_str=API_VERSION, owner=None, workflow_id=None):
        self.api = APIClient(base_url=base_url, version_str=version_str, token=token, owner=owner)
        if not self.api.owner:
            self.api.owner = self.api.get_user_info().user_name
        self.active_workflow = None
        if workflow_id:
            self.active_workflow = Workflow(self.api, self.api.get_workflow(workflow_id))

    @property
    def runs(self):
        """An object for managing runs. See :py:class:`SpellClient.runs <spell.client.runs.RunsService>`."""
        return RunsService(client=self)

    @property
    def hyper(self):
        """An object for managing hyperparameter searches.
        See :py:class:`SpellClient.hyper <spell.client.hyper.HyperService>`.
        """
        return HyperService(client=self)


def from_environment():
    """Creates a :py:class:`SpellClient` object with configuration deduced from the environment.

    First, attempts to find configuration from environment variables:

    .. envvar:: SPELL_TOKEN

        The authentication token for the user.

    .. envvar:: SPELL_OWNER

        The namespace (e.g. user or organization) in which commands should take place.

    .. envvar:: SPELL_WORKFLOW_ID

        An active workflow configuration for setting the workflow context on the returned client.

    Second, attempts to find configuration from an active user session of the Spell CLI.

    Returns:
        A :py:class:`SpellClient` object.

    Raises:
        :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
    """

    token = os.environ.get("SPELL_TOKEN")
    owner = os.environ.get("SPELL_OWNER")
    spell_dir = os.environ.get("SPELL_DIR", default_config_dir())
    base_url = os.environ.get("SPELL_BASE_URL", BASE_URL)

    # parse config file if missing values from environment
    if not all((token, owner)):
        config_handler = ConfigHandler(spell_dir)
        try:
            config_handler.load_config_from_file()
        except ConfigException:
            raise ClientException("Spell configuration not found")

    # populate missing values from config file
    if not token:
        token = config_handler.config.token
    if not owner:
        owner = config_handler.config.owner

    # parse workflow ID
    workflow_id = os.environ.get("SPELL_WORKFLOW_ID")
    if workflow_id:
        try:
            workflow_id = int(workflow_id)
        except ValueError:
            raise ClientException("Invalid environment workflow ID: {}".format(workflow_id))

    return SpellClient(token=token, owner=owner, workflow_id=workflow_id, base_url=base_url)
