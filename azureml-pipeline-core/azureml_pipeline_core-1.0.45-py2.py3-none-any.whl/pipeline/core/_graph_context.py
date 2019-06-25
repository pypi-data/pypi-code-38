# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""_graph_context.py, module for creating a graph context."""
from ._aeva_provider import _AevaWorkflowProvider
from azureml.core import Experiment
from azureml.core.runconfig import LOCAL_RUNCONFIG_NAME
import os


class _GraphContext(object):
    """
    Create a _GraphContext
    """

    def __init__(self, experiment_name, workspace=None, default_source_directory=None,
                 service_endpoint=None, workflow_provider=None):
        """Initializes GraphContext
        :param experiment_name: Experiment name
        :type experiment_name: str
        :param workspace: Workspace _GraphContext will belong to
        :type workspace: Workspace
        :param default_source_directory: Default directory to look for scripts
        :type default_source_directory: str
        :param service_endpoint: Endpoint URI for backend service, if None use dev endpoint
        :type service_endpoint: str
        :param workflow_provider: Workflow Provider, if None a new _AevaWorkflowProvider is created
        :type workflow_provider: _AevaWorkflowProvider
        """
        self._targets = None
        self._experiment_name = experiment_name
        self._experiment = Experiment(workspace, experiment_name)
        if default_source_directory is None:
            # If unspecified, use current working directory as default
            self._default_source_directory = os.getcwd()
        else:
            self._default_source_directory = default_source_directory

        self._workspace = workspace

        self._workflow_provider = workflow_provider
        if self._workflow_provider is None:
            self._workflow_provider = _AevaWorkflowProvider.create_provider(workspace=workspace,
                                                                            experiment_name=experiment_name,
                                                                            service_endpoint=service_endpoint)

    @property
    def default_source_directory(self):
        """
        default location for scripts
        """
        return self._default_source_directory

    def get_target(self, target_name):
        """
        Target object identified by the target name
        """
        if self._targets is None:
            self._targets = self._workspace.compute_targets

        target = self._targets.get(target_name)
        if target is None:
            if target_name == LOCAL_RUNCONFIG_NAME:
                raise ValueError("Please specify a remote compute_target. "
                                 "(Local execution is not supported for pipelines.)")
            else:
                raise ValueError("Target " + target_name + " does not exist in the workspace.")
        return target

    @property
    def workflow_provider(self):
        return self._workflow_provider

    @property
    def experiment_name(self):
        return self._experiment_name

    @experiment_name.setter
    def experiment_name(self, value):
        self._experiment_name = value
        self._experiment = Experiment(self._workspace, self._experiment_name)

    @property
    def service_endpoint(self):
        return self._workflow_provider._service_caller._service_endpoint
