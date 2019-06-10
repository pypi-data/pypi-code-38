# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The **Experiment** class is used to submit new experiments and manage experiment history."""

import logging
from collections import OrderedDict

from azureml._logging import ChainedIdentity
from azureml._project import _commands
from azureml._base_sdk_common.common import check_valid_resource_name
from azureml._restclient.workspace_client import WorkspaceClient

from azureml.core.runconfig import DEFAULT_GPU_IMAGE
from azureml.core._experiment_method import get_experiment_submit
from azureml.core._portal import HasExperimentPortal
from azureml.core._docs import get_docs_url
from azureml._html.utilities import to_html, make_link

module_logger = logging.getLogger(__name__)


class Experiment(ChainedIdentity, HasExperimentPortal):
    """The main entry point into experimenting with Azure Machine Learning service.

    The class acts as a container of *trials* that represent multiple model runs.

    .. remarks::

        An Azure Machine Learning *experiment* represent the collection of *trials* used to validate a
        user's *hypothesis*.

        In Azure Machine Learning, an experiment is represented by the :class:`azureml.core.Experiment`
        class and a trial is represented by the :class:`azureml.core.Run` class.

        To get or create an experiment from a workspace, you request the experiment using the experiment name.
        Experiment name must be 3-36 characters, start with a letter or a number, and can only contain letters,
        numbers, underscores, and dashes.

        .. code-block:: python

            experiment = Experiment(workspace, "MyExperiment")

        If the experiment is not found in the workspace, a new experiment is created when an experiment trial
        is executed.

        There are two ways to execute an experiment trial. If you are interactively experimenting in a
        Jupyter notebook, use  :func:`start_logging` If you are submitting an experiment from source code
        or some other type of configured trial, use :func:`submit`

        Both mechanisms create a :class:`azureml.core.Run` object.  In interactive scenarios, use logging methods
        such as :func:`azureml.core.Run.log` to add measurements and metrics to the trial record.  In configured
        scenarios use status methods such as :func:`azureml.core.Run.get_status` to retrieve information about the
        run.

        In both cases you can use query methods like :func:`azureml.core.Run.get_metrics` to retrieve the current
        values, if any, of any trial measurements and metrics.


    :param workspace: The workspace object containing the experiment.
    :type workspace: azureml.core.workspace.Workspace
    :param name: The experiment name.
    :type name: str
    :param kwargs:
    :type kwargs: dict
    """

    def __init__(self, workspace, name, _skip_name_validation=False, **kwargs):
        """Experiment constructor.

        :param workspace: The workspace object containing the experiment.
        :type workspace: azureml.core.workspace.Workspace
        :param name: The experiment name.
        :type name: str
        :param kwargs:
        :type kwargs: dict
        """
        self._workspace = workspace
        self._name = name

        _ident = kwargs.pop("_ident", ChainedIdentity.DELIM.join([self.__class__.__name__, self._name]))

        if not _skip_name_validation:
            check_valid_resource_name(name, "Experiment")

        super(Experiment, self).__init__(experiment=self, _ident=_ident, **kwargs)

    def submit(self, config, tags=None, **kwargs):
        """Submit an experiment and return the active created run.

        .. remarks::

            Submit is an asynchronous call to the Azure Machine Learning platform to execute a trial on local
            or remote hardware.  Depending on the configuration, submit will automatically prepare
            your execution environments, execute your code, and capture your source code and results
            into the experiment's run history.

            To submit an experiment you first need to create a configuration object describing
            how the experiment is to be run.  The configuration depends on the type of trial required.

            An example of how to submit an experiment from your local machine is as follows:

            .. code-block:: python

                from azureml.core import ScriptRunConfig

                # run a trial from the train.py code in your current directory
                config = ScriptRunConfig(source_directory='.', script='train.py',
                    run_config=RunConfiguration())
                run = experiment.submit(config)

                # get the url to view the progress of the experiment and then wait
                # until the trial is complete
                print(run.get_portal_url())
                run.wait_for_completion()

            For details on how to configure a run, see the configuration type details.

            * :class:`azureml.core.ScriptRunConfig`
            * :class:`azureml.train.automl.AutoMLConfig`
            * :class:`azureml.pipeline.core.Pipeline`
            * :class:`azureml.pipeline.core.PublishedPipeline`
            * :class:`azureml.pipeline.core.PipelineEndpoint`

        :param config: The config to be submitted
        :type config: object
        :param tags: Tags to be added to the submitted run, {"tag": "value"}
        :type tags: dict
        :param kwargs:
        :type kwargs: dict
        :return: run
        :rtype: azureml.core.Run
        """
        # Warn user if trying to run GPU image on a local machine
        try:
            runconfig = config.run_config
            if (runconfig.environment.docker.base_image == DEFAULT_GPU_IMAGE and runconfig.target == "local"):
                print("Note: The GPU base image must be used on Microsoft Azure Services only. See LICENSE.txt file.")
        except AttributeError:  # Not all configuration options have run_configs that specify base images
            pass

        submit_func = get_experiment_submit(config)
        with self._log_context("submit config {}".format(config.__class__.__name__)):
            run = submit_func(config, self.workspace, self.name, **kwargs)
        if tags is not None:
            run.set_tags(tags)
        return run

    def start_logging(self, *args, **kwargs):
        """Start an interactive logging session in the specified experiment.

        .. remarks::

            **start_logging** creates an interactive run for use in scenarios such as Jupyter notebooks.
            Any metrics that are logged during the session are added to the run record in the experiment.
            If an output directory is specified, the contents of that directory is uploaded as run
            artifacts upon run completion.

            .. code-block:: python

                experiment = Experiment(workspace, "My Experiment")
                run = experiment.start_logging()
                ...
                run.log_metric("Accuracy", accuracy)
                run.complete()

            .. note::

                *run_id* and *name* are not typically specified.  *run_id* is automatically
                generated for each run and is unique within the experiment; *name* is typically
                used only for child run scenarios where a run has distinct "parts".

        :param experiment: The experiment.
        :type experiment: azureml.core.Experiment
        :param args:
        :type args: :py:class:`list`
        :param kwargs:
        :type kwargs: dict
        :return: Return a started run.
        :rtype: azureml.core.Run
        """
        from azureml.core.run import Run
        return Run._start_logging(self, *args, _parent_logger=self._logger, **kwargs)

    @staticmethod
    def from_directory(path, auth=None):
        """(Deprecated) Load an experiment from the specified path.

        :param path: Directory containing the experiment configuration files
        :type path: str
        :param auth: The auth object.
            If None the default Azure CLI credentials will be used or the API will prompt for credentials.
        :type auth: azureml.core.authentication.ServicePrincipalAuthentication or
            azureml.core.authentication.InteractiveLoginAuthentication
        :return: Returns the Experiment
        :rtype: azureml.core.Experiment
        """
        from azureml.core.workspace import Workspace

        info_dict = _commands.get_project_info(auth, path)

        # TODO: Fix this
        subscription = info_dict[_commands.SUBSCRIPTION_KEY]
        resource_group_name = info_dict[_commands.RESOURCE_GROUP_KEY]
        workspace_name = info_dict[_commands.WORKSPACE_KEY]
        experiment_name = info_dict[_commands.PROJECT_KEY]

        workspace = Workspace(
            subscription_id=subscription, resource_group=resource_group_name, workspace_name=workspace_name, auth=auth
        )
        return Experiment(workspace, experiment_name)

    @property
    def workspace(self):
        """Return the workspace containing the experiment.

        :return: Returns the workspace object.
        :rtype: azureml.core.workspace.Workspace
        """
        return self._workspace

    @property
    def workspace_object(self):
        """(Deprecated) Return the workspace containing the experiment.

        :return: The workspace object.
        :rtype: azureml.core.workspace.Workspace
        """
        self._logger.warning("Deprecated, use experiment.workspace")
        return self.workspace

    @property
    def name(self):
        """Return name of the experiment.

        :return: The name of the experiment.
        :rtype: str
        """
        return self._name

    def get_runs(self, type=None, tags=None, properties=None, include_children=False):
        """Return a generator of the runs for this experiment, in reverse chronological order.

        :param type: Filter the returned generator of runs by the provided type. See
            :func:`azureml.core.Run.add_type_provider` for creating run types.
        :type type: string
        :param tags: Filter runs by "tag" or {"tag": "value"}
        :type tags: string or dict
        :param properties: Filter runs by "property" or {"property": "value"}
        :type properties: string or dict
        :param include_children: By default, fetch only top-level runs. Set to true to list all runs
        :type include_children: bool
        :return: The list of runs matching supplied filters
        :rtype: generator[azureml.core.Run]
        """
        from azureml.core.run import Run
        return Run.list(self, type=type, tags=tags, properties=properties, include_children=include_children)

    @staticmethod
    def list(workspace):
        """Return the list of experiments in the workspace.

        :param workspace: The workspace from which to list the experiments..
        :type workspace: azureml.core.workspace.Workspace
        :return: list of experiment objects.
        :rtype: :py:class:`list[azureml.core.Experiment]`
        """
        workspace_client = WorkspaceClient(workspace.service_context)
        experiments = workspace_client.list_experiments()
        return [Experiment(workspace, experiment.name, _skip_name_validation=True) for experiment in experiments]

    def _serialize_to_dict(self):
        """Serialize the Experiment object details into a dictionary.

        :return: experiment details
        :rtype: dict
        """
        output_dict = {"Experiment name": self.name,
                       "Subscription id": self.workspace.subscription_id,
                       "Resource group": self.workspace.resource_group,
                       "Workspace name": self.workspace.name}
        return output_dict

    def _get_base_info_dict(self):
        """Return base info dictionary.

        :return:
        :rtype: OrderedDict
        """
        return OrderedDict([
            ('Name', self._name),
            ('Workspace', self._workspace.name)
        ])

    @classmethod
    def get_docs_url(cls):
        """Url to the documentation for this class.

        :return: url
        :rtype: str
        """
        return get_docs_url(cls)

    def __str__(self):
        """Format Experiment data into a string.

        :return:
        :rtype: str
        """
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Experiment({0})".format(formatted_info)

    def __repr__(self):
        """Representation of the object.

        :return: Return the string form of the experiment object
        :rtype: str
        """
        return self.__str__()

    def _repr_html_(self):
        """Html representation of the object.

        :return: Return an html table representing this experiment
        :rtype: str
        """
        info = self._get_base_info_dict()
        info.update([
            ('Report Page', make_link(self.get_portal_url(), "Link to Azure Portal")),
            ('Docs Page', make_link(self.get_docs_url(), "Link to Documentation"))
        ])
        return to_html(info)
