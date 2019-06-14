from spell.client.model import SpellModel


class Workspace(SpellModel):
    """An object representing a single Spell workspace.

    Attributes:
        id (int): the workspace id
        root_commit (str): the root commit of the workspace repository
        name (str): the workspace name
        description (str): the workspace description
        git_remote_url (str): the Spell git remote URL for the repository
        created_at (:py:class:`datetime.datetime`): the workspace creation time
        updated_at (:py:class:`datetime.datetime`): the workspace last update time
    """

    model = "workspace"

    def __init__(self, api, workspace):
        self._api = api
        self.workspace = workspace
