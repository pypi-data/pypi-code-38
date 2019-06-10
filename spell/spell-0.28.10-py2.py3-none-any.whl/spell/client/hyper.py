from spell.api.models import RunRequest
from spell.client.model import SpellModel
from spell.client.utils import read_conda_env_contents
from spell.client.runs import Run

from spell.api.models import RangeSpec, ValueSpec # noqa
from spell.api.models import LINEAR, LOG, REVERSE_LOG, INT, FLOAT


class HyperService(object):
    """An object for managing Spell hyperparameter searches."""

    def __init__(self, client):
        self.client = client

    def new_grid_search(self, params, **kwargs):
        """Create a hyperparameter grid search.

        Args:
            params (:obj:`dict` of :obj:`str` -> :py:class:`ValueSpec`): hyperparameter
                specifications for the run. A run will be created for all hyperparameter value combinations provided.
                Each key of the :obj:`dict` should appear in the :obj:`command` argument surrounded by colons.
            **kwargs: all keyword arguments for a new run are accepted here.
                See :py:class:`~spell.runs.RunsService.new`.
        Returns:
            A :py:class:`HyperSearch` object

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        # grab conda env file contents
        conda_env_contents = read_conda_env_contents(kwargs.pop("conda_file", None))

        # set workflow id
        workflow_id = kwargs.pop("workflow_id", None)
        if self.client.active_workflow:
            workflow_id = self.client.active_workflow.id
        # create run request
        run_req = RunRequest(run_type="user", conda_file=conda_env_contents,
                             workflow_id=workflow_id, **kwargs)
        hyper = self.client.api.hyper_grid_search(params, run_req)
        return HyperSearch(self.client.api, hyper)

    def new_random_search(self, params, num_runs, **kwargs):
        """Create a hyperparameter random search.

        Args:
            params (:obj:`dict` of :obj:`str` -> :py:class:`ValueSpec` or :py:class:`RangeSpec`): hyperparameter
                specifications for the run. :obj:`num_runs` runs will be created and each hyperparameter
                specified will be sampled to determine a specific value for each run.
                Each key of the :obj:`dict` should appear in the :obj:`command` argument surrounded by colons.
            num_runs (int): the number of runs to create in this hyperparameter search
            **kwargs: all keyword arguments for a new run are accepted here.
                See :py:class:`~spell.runs.RunsService.new`.
        Returns:
            A :py:class:`HyperSearch` object

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        # grab conda env file contents
        conda_env_contents = read_conda_env_contents(kwargs.pop("conda_file", None))

        # set workflow id
        workflow_id = kwargs.pop("workflow_id", None)
        if self.client.active_workflow:
            workflow_id = self.client.active_workflow.id
        # create run request
        run_req = RunRequest(run_type="user", conda_file=conda_env_contents,
                             workflow_id=workflow_id, **kwargs)
        hyper = self.client.api.hyper_random_search(params, num_runs, run_req)
        return HyperSearch(self.client.api, hyper)

    #: str : a constant for the "linear" hyperparameter scaling
    LINEAR = LINEAR
    #: str : a constant for the "log" hyperparameter scaling
    LOG = LOG
    #: str : a constant for the "reverse_log" hyperparameter scaling
    REVERSE_LOG = REVERSE_LOG

    #: str : a constant for the "float" hyperparameter type
    FLOAT = FLOAT
    #: str : a constant for the "int" hyperparameter type
    INT = INT


class HyperSearch(SpellModel):
    """An object representing a hyperparameter search.

    Attributes:
        id (int) : the hyperparameter search id
        runs (:obj:`list` of :py:class:`Run`): the runs created by the hyperparameter search
    """

    model = "hyper"

    def __init__(self, api, hyper):
        self._api = api
        self.hyper = hyper
        self.runs = [Run(api, run) for run in hyper.runs]

    def refresh(self):
        """Refresh the hyperparameter search state.

        Refresh all of the hyperparameter search attributes with the latest information for the
        hyperparameter search from Spell.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        hyper = self._api.get_hyper_search(self.id)
        self.runs = [Run(self._api, run) for run in hyper.runs]
        self.hyper = hyper

    def stop(self):
        """Stop the hyperparameter search.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        self._api.stop_hyper_search(self.id)

    def kill(self):
        """Kill the hyperparameter search.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        self._api.kill_hyper_search(self.id)
