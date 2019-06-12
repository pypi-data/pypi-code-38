from spell.client.model import SpellModel


class Workflow(SpellModel):
    """An object representing a single Spell workflow.

    Attributes:
        id (int): the workflow id
        workspace_specs (:obj:`dict` of :obj:`str` -> :obj:`dict`): label to workspace spec mapping
            of git commits associated with the workflow
        managing_run (:py:class:`~spell.client.runs.Run`): the remote run executing the workflow command
        runs (:obj:`list` of :py:class:`~spell.client.runs.Run`): runs created within the workflow
    """

    model = "workflow"

    def __init__(self, api, workflow):
        self._api = api
        self.workflow = workflow

    def refresh(self):
        """Refresh the workflow state.

        Refresh all of the workflow attributes with the latest information for the workflow
        from Spell.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        self.workflow = self._api.get_workflow(self.id)
