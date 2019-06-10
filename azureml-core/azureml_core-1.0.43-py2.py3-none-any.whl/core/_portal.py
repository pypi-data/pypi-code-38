# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging


def _warn_on_preview_url(url):
    # type: (str) -> bool
    if "azureml-test.net" in url or "history" in url:
        logging.warn("URL is not final public url")


class HasPortal(object):
    """ Mixin protocol providing Azure Portal links for workspaces """

    def get_portal_url(self):
        raise NotImplementedError("No portal URL implemented")


class HasWorkspacePortal(HasPortal):
    """
    Mixin for providing Azure Portal links for workspaces.
    :param workspace:
    :type workspace: Workspace
    """

    PORTAL_URL = 'https://mlworkspace.azure.ai/portal'
    WORKSPACE_FMT = PORTAL_URL +\
        '/subscriptions/{0}' \
        '/resourceGroups/{1}' \
        '/providers' \
        '/Microsoft.MachineLearningServices' \
        '/workspaces/{2}'

    def __init__(self, workspace):
        """ The constructor method """
        self._workspace_url = HasWorkspacePortal.WORKSPACE_FMT.format(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name)

    def get_portal_url(self):
        """
        :return: Returns the Azure portal url for the workspace.
        :rtype: str
        """
        # type () -> str
        _warn_on_preview_url(self._workspace_url)
        return self._workspace_url


class HasExperimentPortal(HasWorkspacePortal):
    """
    Mixin for providing experiment links to the Azure portal.
    :param experiment:
    :type experiment: Experiment
    """

    EXPERIMENT_PATH = '/experiments/{0}'

    def __init__(self, experiment):
        """ The constructor method """
        super(HasExperimentPortal, self).__init__(workspace=experiment.workspace)
        self._experiment_url = self._workspace_url + HasExperimentPortal.EXPERIMENT_PATH.format(experiment.name)

    def get_portal_url(self):
        """
        :return: Returns the Azure portal url for the experiment.
        :rtype: str
        """
        # type () -> str
        _warn_on_preview_url(self._experiment_url)
        return self._experiment_url


class HasRunPortal(HasExperimentPortal):
    """
    Mixin for providing run links to the Azure portal.
    :param experiment:
    :type experiment: Experiment
    :param run_id:
    :type run_id: str
    """

    RUN_PATH = '/runs/{0}'

    def __init__(self, experiment, run_id):
        """ The constructor method """
        super(HasRunPortal, self).__init__(experiment=experiment)
        self._run_details_url = self._experiment_url + HasRunPortal.RUN_PATH.format(run_id)

    def get_portal_url(self):
        """
        :return: Returns the Azure portal url for the experiment.
        :rtype: str
        """
        # type () -> str
        _warn_on_preview_url(self._run_details_url)
        return self._run_details_url


class HasPipelinePortal(HasWorkspacePortal):
    """
    Mixin for providing pipeline links to the Azure portal.
    :param pipeline:
    :type pipeline: Pipeline
    """

    PIPELINE_PATH = '/pipelines/{0}'

    def __init__(self, pipeline):
        """ The constructor method """
        super(HasPipelinePortal, self).__init__(workspace=pipeline.workspace)
        self._pipeline_url = self._workspace_url + HasPipelinePortal.PIPELINE_PATH.format(pipeline.id)

    def get_portal_url(self):
        """
        :return: Returns the Azure portal url for the pipeline.
        :rtype: str
        """
        # type () -> str
        _warn_on_preview_url(self._pipeline_url)
        return self._pipeline_url
