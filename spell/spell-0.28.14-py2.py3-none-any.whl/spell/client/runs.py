import os
import stat

from spell.api.models import RunRequest
from spell.client.model import SpellModel
from spell.client.workspaces import Workspace
from spell.client.utils import read_conda_env_contents


class RunsService(object):
    """An object for managing Spell runs."""

    def __init__(self, client):
        self.client = client

    def new(self, **kwargs):
        """Create a run.

        Args:
            command (str): the command to run
            machine_type (str, optional): the machine type for the run (default: CPU)
            workspace_id (int, optional): the workspace ID for code to include in the run (default: None)
            commit_hash (str, optional): a specific commit hash in the workspace corresponding to :obj:`workspace_id`
                for code to include in the run (default: None)
            commit_label (str, optional): a commit label for code to include in the run. Only applicable
                if this is a workflow run (i.e., the :py:attr:`~spell.client.SpellClient.active_workflow` of the
                client is set or a :obj:`workflow_id` is provided) (default: None). The value must correspond
                to one of the commit labels specified upon workflow creation using the ``--repo`` option.
                Only applicable if a workspace is specified.
            github_url (str, optional): a GitHub URL to a repository for code to include in the run. Not applicable
                when :obj:`workspace_id` or :obj:`commit_label` is specified.
            github_ref (str, optional): a reference to a commit, branch, or tag in the repository corresponding to
                :obj:`github_url` for code to include in the run (default: master)
            pip_packages (:obj:`list` of :obj:`str`, optional): pip dependencies (default: None).
                For example: ``["moviepy", "scikit-image"]``
            apt_packages (:obj:`list` of :obj:`str`, optional): apt dependencies (default: None).
                For example: ``["python-tk", "ffmpeg"]``
            envvars (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): name to value mapping of
                environment variables for the run (default: None).
                For example: ``{"VARIABLE" : "VALUE", "LANG" : "C.UTF-8"}``
            cwd (str, optional): the working directory within the repository in which to execute the command
                (default: None). Only applicable if a workspace is specified.
            python2 (bool, optional): set the python version to python 2 (default: false)
            conda_file (str, optional): the path to a conda specification file or YAML environment file (default: None).
            docker_image (str, optional): the name of docker image to use as base (default: None)
            framework (str, optional): the framework to use for the run (default: None). For example: ``pytorch``
            framework_version (str, optional): the framework version to use for the run (default: None).
                For example: ``0.2.0``
            attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`, optional): resource name to
                mountpoint mapping of attached resouces for the run (default: None).
                For example: ``{"runs/42" : "/mnt/data"}``
            description (str, optional): a description for the run (default: None)
            idempotent (bool, optional): use an existing identical run if available in lieu of re-running
                (default: false)
            workflow_id (int, optional): the id of the workflow to which this run will be associated (default: None).
                This argument is unnecessary if the :py:attr:`~spell.client.SpellClient.active_workflow` of
                the client is set and this argument will take precedence if they differ.

        Returns:
            A :py:class:`Run` object.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        # grab conda env file contents
        conda_env_contents = read_conda_env_contents(kwargs.pop("conda_file", None))

        # set workflow id
        workflow_id = None
        if kwargs.get("workflow_id"):
            workflow_id = kwargs.pop("workflow_id")
        elif self.client.active_workflow:
            workflow_id = self.client.active_workflow.id
        # create request
        run_req = RunRequest(run_type="user", conda_file=conda_env_contents,
                             workflow_id=workflow_id, **kwargs)
        run = self.client.api.run(run_req)
        return Run(self.client.api, run)

    #: str : a constant for the "building" state
    BUILDING = "building"
    #: str : a constant for the "running" state
    RUNNING = "running"
    #: str : a constant for the "saving" state
    SAVING = "saving"
    #: str : a constant for the "pushing" state
    PUSHING = "pushing"
    #: str : a constant for the "complete" state
    COMPLETE = "complete"
    #: str : a constant for the "failed" state
    FAILED = "failed"
    #: str : a constant for the "stopped" state
    STOPPED = "stopped"
    #: str : a constant for the "killed" state
    KILLED = "killed"
    #: :obj:`tuple` of :obj:`str`: a tuple of the constants for the final states
    #: (i.e., :obj:`COMPLETE`, :obj:`FAILED`, :obj:`STOPPED`, and :obj:`KILLED`)
    FINAL = (COMPLETE, FAILED, STOPPED, KILLED)
    #: str : a constant for the equals condition (i.e. metric == b)
    EQUALS = "eq"
    #: str : a constant for the greater than condition (i.e. metric > b)
    GREATER_THAN = "gt"
    #: str : a constant for the greater than or equals condition (i.e. metric >= b)
    GREATER_THAN_EQUALS = "gte"
    #: str : a constant for the less than condition (i.e. metric < b)
    LESS_THAN = "lt"
    #: str : a constant for the less than or equals condition (i.e., metric <= b)
    LESS_THAN_EQUALS = "lte"


class Run(SpellModel):
    """An object representing a single Spell run.

    Attributes:
        id (int) : the run id
        status (str): the run status
        user_exit_code (int): the exit code of :obj:`command`
        command (str): the run command
        gpu (str): the GPU the run executed on
        git_commit_hash (str): the commit hash of the workspace repository for the run
        github_url (str): the URL of the GitHub repo used in the run
        description (str): the run description
        docker_image (str): the run docker image
        framework (str): the Spell framework for the run
        created_at (:py:class:`datetime.datetime`): the run creation time
        started_at (:py:class:`datetime.datetime`): the run start time
        ended_at (:py:class:`datetime.datetime`): the run end time
        workspace (:py:class:`~spell.client.workspaces.Workspace`): the run workspace
        pip_packages (:obj:`list` of :obj:`str`): pip dependencies
        apt_packages (:obj:`list` of :obj:`str`): apt dependencies
        attached_resources (:obj:`dict` of :obj:`str` -> :obj:`str`): resource name to
            mountpoint mapping of attached resouces for the run
        environment_vars (:obj:`dict` of :obj:`str` -> :obj:`str`): name to value mapping of
            environment variables for the run
        already_existed (bool): true if an existing identical run was used in lieu of re-running
    """

    model = "run"

    def __init__(self, api, run):
        self._api = api
        self.run = run
        if run.workspace:
            self.workspace = Workspace(api, run.workspace)

    def stop(self):
        """Stop the run.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        self._api.stop_run(self.id)

    def kill(self):
        """Kill the run.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.
        """
        self._api.kill_run(self.id)

    def refresh(self):
        """Refresh the run state.

        Refresh all of the run attributes with the latest information for the run
        from Spell.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.

        Example:
            >>> r.status
            'machine_requested'
            >>> r.refresh()
            >>> r.status
            'running'
        """
        self.run = self._api.get_run(self.id)

    def wait_status(self, *statuses):
        """Wait until the run achieves one of the given statuses and then return.

        Args:
            *statuses (required): variable length list of statuses to wait for. Allowed values are
                :py:attr:`~RunsService.BUILDING`, :py:attr:`~RunsService.RUNNING`, :py:attr:`~RunsService.SAVING`,
                :py:attr:`~RunsService.SAVING`, :py:attr:`~RunsService.PUSHING`, :py:attr:`~RunsService.COMPLETE`,
                :py:attr:`~RunsService.FAILED`, :py:attr:`~RunsService.STOPPED`, :py:attr:`~RunsService.KILLED`,

        Raises:
            :py:class:`~spell.api.exceptions.WaitError` if none of the given statuses are reached.
            :py:class:`~spell.api.exceptions.ClientException` if any other error occurs.

        Example:
            >>> client = spell.client.from_environment()
            >>> r = client.runs.run(command="sleep 20", machine_type="CPU")
            >>> r.wait_status(client.runs.BUILDING)
            >>> r.wait_status(*client.runs.FINAL)
        """
        self._api.wait_status(self.id, *statuses)

    def wait_metric(self, metric_name, condition, value):
        """Wait until the run metric reaches the given condition and then return

        Args:
            metric_name (str): the name of the user metric
            condition(str): the condition to wait for. Allowed values are
                :py:attr:`~RunsService.EQUALS`, :py:attr:`~RunsService.GREATER_THAN`,
                :py:attr:`~RunsService.GREATER_THAN_EQUALS`, :py:attr:`~RunsService.LESS_THAN`,
                :py:attr:`~RunsService.LESS_THAN_EQUALS`,
            value (int, float, or str): the value to evaluate the condition against

        Raises:
            :py:class:`~spell.api.exceptions.WaitError` if the condition is never reached
            :py:class:`~spell.api.exceptions.ClientException` if any other error occurs.
        """
        self._api.wait_metric(self.id, metric_name, condition, value)

    def metrics(self, metric_name, follow=False, start=None):
        """Get metrics for the run.

        Args:
            metric_name (str): the name of the user metric
            start(:py:class:`datetime.datetime`, optional): the offset to start at. (default: None)
                A value of :py:obj:`None` will start from the oldest metric. This is an exclusive
                offset, so only metrics with timestamp greater than offset will be returned.
            follow (bool, optional): follow the metrics until the run reaches a final status (default: False)

        Yields:
            A 3-tuple of (``timestamp``, ``index``, ``value``) for each metric.
            ``timestamp`` is a :py:class:`datetime.datetime` object, ``index`` is a
            :py:obj:`int`, and ``value`` is one of :py:obj:`int`, :py:obj:`float`, or :py:obj:`str`.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if any other error occurs.
        """
        return self._api.get_run_metrics(self.id, metric_name, follow, start)

    def logs(self, follow=False, offset=0):
        """Get the logs for the run.

        A generator of log entries (:py:class:`~spell.api.models.LogEntry` objects).  Each log
        entry  corresponds to either an informational message from Spell regarding run status
        or any line from standard out or standard error that resulted from executing the run
        command.

        Args:
            follow (bool, optional): follow the log lines until the run reaches a final status (default: False)
            offset (int, optional): which log line to start from. Negative values represent offsets
                relative to the latest log line (default: 0)

        Yields:
            A :py:class:`~spell.api.models.LogEntry` object for each log line.

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.

        Example:
            >>> client = spell.client.from_environment()
            >>> run = client.runs.run(command="echo 'HELLO!!!!'", machine_type="CPU")
            >>> for line in run.logs():
                ...     print(line)
                ...
                Run created -- waiting for a CPU machine.
                Run is building
                Machine acquired -- commencing run
                Run is running
                Retrieving cached environment...
                HELLO!!!!
                Run is saving
                Retrieving modified or new files from the run
                No modified or new files found
        """
        for line in self._api.get_run_log_entries(self.id, follow=follow, offset=offset):
            yield line

    def cp(self, source_path="", destination_directory=None):
        """Copy a file or directory from the run to local disk.

        Args:
            source_path (str, optional): the path within the run to copy
                (default: empty string, i.e., copy everything from the run)
            destination_directory (str, optional): destination directory to copy the file or directory to
                (default: the current working directory)

        Raises:
            :py:class:`~spell.api.exceptions.ClientException` if an error occurs.

        Example:
            >>> client = spell.client.from_environment()
            >>> run = client.runs.run(command="echo contents > file", machine_type="CPU")
            >>> run.wait_status(client.runs.COMPLETE)
            >>> run.cp("file")
            >>> with open("file") as f:
                ...     print(f.read())
                ...
                contents
        """
        if not destination_directory:
            destination_directory = os.getcwd()
        source_path = "runs/{}/{}".format(self.id, source_path)
        with self._api.tar_of_path(source_path) as tar:
            for file in tar:
                if file.isdir() and not (file.mode & stat.S_IXUSR):
                    # Workaround for early uploads missing execute bit on directories, which breaks `ls`
                    file.mode |= stat.S_IXUSR
                tar.extract(file, path=destination_directory)

    # TODO(Brian): complete rest of Run object methods.....ls, etc.
