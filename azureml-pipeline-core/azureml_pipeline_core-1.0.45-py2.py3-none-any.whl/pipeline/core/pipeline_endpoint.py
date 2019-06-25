# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""pipeline_endpoint.py, module for managing pipelines."""
from __future__ import print_function
from azureml._html.utilities import to_html, make_link
from collections import OrderedDict
from azureml.core._experiment_method import experiment_method
from azureml.pipeline.core.run import PipelineRun
from azureml.pipeline.core.graph import PublishedPipeline
import uuid
import logging
from datetime import datetime


def _submit_pipeline_endpoint(pipeline_endpoint, experiment_name, **kwargs):
    """
    Submit a PipelineEndpoint.

    :param pipeline_endpoint: PipelineEndpoint
    :type pipeline_endpoint: PipelineEndpoint
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    pipeline_params = None
    parent_run_id = None
    pipeline_version = None
    for key, value in kwargs.items():
        if key == 'pipeline_params':
            pipeline_params = value
        elif key == 'parent_run_id':
            parent_run_id = value
        elif key == 'pipeline_version':
            pipeline_version = value

    return pipeline_endpoint.submit(experiment_name=experiment_name, pipeline_parameters=pipeline_params,
                                    parent_run_id=parent_run_id, pipeline_version=pipeline_version)


class PipelineEndpoint(object):
    """
    A PipelineEndpoint represents a Pipeline workflow that can be triggered from a unique endpoint URL.

    PipelineEndpoints can be used to create new versions of a :class:`azureml.pipeline.core.PublishedPipeline`
    while maintaining the same endpoint. PipelineEndpoints are uniquely named within a workspace.

    .. remarks::

        A PipelineEndpoint can be created from either a :class:`azureml.pipeline.core.Pipeline`
        or a :class:`azureml.pipeline.core.PublishedPipeline`.

        An example to publish from a Pipeline or PublishedPipeline is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineEndpoint

            # The pipeline argument can be either a Pipeline or a PublishedPipeline
            pipeline_endpoint = PipelineEndpoint.publish(workspace=ws,
                                                         name="PipelineEndpointName",
                                                         pipeline=pipeline,
                                                         description="New Pipeline Endpoint")

        Submit a PipelineEndpoint using :func:`azureml.core.Experiment.submit`. When submit is called,
        a :class:`azureml.pipeline.core.PipelineRun` is created which in turn creates
        :class:`azureml.pipeline.core.StepRun` objects for each step in the workflow.

        An example to submit a PipelineEndpoint is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineEndpoint

            pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name="PipelineEndpointName")
            pipeline_run = experiment.submit(pipeline_endpoint)

        There are a number of optional settings that can be specified when submitting a PipelineEndpoint.
        These include:

        *  pipeline_params: Parameters to pipeline execution, dictionary of {name: value}.
                            See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        *  parent_run_id: You can supply the run id to set the parent run of this pipeline run.
        *  pipeline_version: The pipeline version to run.

        An example to submit a PipelineEndpoint using these settings is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineEndpoint

            pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name="PipelineEndpointName")
            pipeline_run = experiment.submit(pipeline_endpoint,
                                             pipeline_params={"param1": "value1"},
                                             parent_run_id="<run_id>",
                                             pipeline_version="0")

        To add a new version of a PipelineEndpoint use:

        .. code-block:: python

            from azureml.pipeline.core import PipelineEndpoint

            pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name="PipelineEndpointName")
            pipeline_endpoint.add(published_pipeline)

        See the following notebook for additional information on creating and using PipelineEndpoints:
        https://aka.ms/pl-ver-endpoint

    :param workspace: Workspace object this PipelineEndpoint will belong to.
    :type workspace: azureml.core.Workspace
    :param id: The Id of the PipelineEndpoint.
    :type id: str
    :param name: The name of the PipelineEndpoint.
    :type name: str
    :param description: Description of the PipelineEndpoint.
    :type description: str
    :param status: The new status of the PipelineEndpoint: 'Active' or 'Disabled'.
    :type status: str
    :param endpoint: REST endpoint URL for pipelineEndpoint to submit pipeline runs.
    :type endpoint: str
    :param default_version: The default version of the PipelineEndpoint.
    :type default_version: str
    :param pipeline_version_list: The list of :class:`azureml.pipeline.core.pipeline_endpoint.PipelineIdVersion`
    :type pipeline_version_list: :class:`list`
    :param _pipeline_endpoint_provider: The PipelineEndpoint provider.
    :type _pipeline_endpoint_provider: _AevaPipelineEndpointProvider object
    :param _pipeline_endpoint_provider: The PublishedPipeline provider.
    :type _pipeline_endpoint_provider: _AevaPublishedPipelineProvider object
    """

    @experiment_method(submit_function=_submit_pipeline_endpoint)
    def __init__(self, workspace, id, name, description, status, default_version, endpoint, pipeline_version_list,
                 _pipeline_endpoint_provider=None, _published_pipeline_provider=None):
        """
        Initialize PipelineEndpoint.

        :param workspace: Workspace object this PipelineEndpoint will belong to.
        :type workspace: azureml.core.Workspace
        :param id: The Id of the PipelineEndpoint.
        :type id: str
        :param name: The name of the PipelineEndpoint.
        :type name: str
        :param description: Description of the PipelineEndpoint.
        :type description: str
        :param status: The new status of the PipelineEndpoint: 'Active' or 'Disabled'.
        :type status: str
        :param default_version: The default version of the PipelineEndpoint.
        :type default_version: str
        :param endpoint: REST endpoint URL for pipelineEndpoint to submit pipeline runs.
        :type endpoint: str
        :param pipeline_version_list: The list of :class:`azureml.pipeline.core.pipeline_endpoint.PipelineIdVersion`
        :type pipeline_version_list: :class:`list`
        :param _pipeline_endpoint_provider: The PipelineEndpoint provider.
        :type _pipeline_endpoint_provider: _AevaPipelineEndpointProvider object
        :param _pipeline_endpoint_provider: The PublishedPipeline provider.
        :type _pipeline_endpoint_provider: _AevaPublishedPipelineProvider object
        """
        self._workspace = workspace
        self._id = id
        self._name = name
        self._description = description
        self._status = status
        self._default_version = default_version
        self._endpoint = endpoint
        self._pipeline_version_list = pipeline_version_list
        self._workspace = workspace
        self._pipeline_endpoint_provider = _pipeline_endpoint_provider
        self._published_pipeline_provider = _published_pipeline_provider

    @property
    def id(self):
        """
        Id of the PipelineEndpoint.

        :return: The id.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        """
        Name of the PipelineEndpoint.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the PipelineEndpoint.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def status(self):
        """
        Get the status of the PipelineEndpoint.

        :return: The status.
        :rtype: str
        """
        return self._status

    @property
    def default_version(self):
        """
        Get the default version of the PipelineEndpoint.

        :return: The default version string.
        :rtype: str
        """
        return self._default_version

    @property
    def endpoint(self):
        """
        Get REST endpoint URL of the PipelineEndpoint to trigger run of pipeline.

        :return: REST endpoint for PipelineEndpoint to run pipeline
        :rtype: str
        """
        return self._endpoint

    @property
    def pipeline_version_list(self):
        """
        Get the pipeline version list.

        :return: The list of :class:`azureml.pipeline.core.pipeline_endpoint.PipelineIdVersion`
        :rtype: :class:`list`
        """
        return self._pipeline_version_list

    @staticmethod
    def publish(workspace, name, description, pipeline,
                _workflow_provider=None, _service_endpoint=None):
        """
        Create a PipelineEndpoint.

        Create a PipelineEndpoint with given name and pipeline/published pipeline.
        Throws Exception, if PipelineEndpoint with given name already exist.

        :param workspace: Workspace object this PipelineEndpoint will belong to.
        :type workspace: azureml.core.Workspace
        :param name: The name of the PipelineEndpoint.
        :type name: str
        :param description: The name of the PipelineEndpoint.
        :type description: str
        :param pipeline: The published pipeline or pipeline
        :type pipeline: azureml.pipeline.core.graph.PublishedPipeline or
            azureml.pipeline.core.Pipeline
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :return: The created PipelineEndpoint.
        :rtype: azureml.pipeline.core.PipelineEndpoint
        """
        from azureml.pipeline.core import Pipeline
        if type(pipeline) not in [Pipeline, PublishedPipeline]:
            raise ValueError("pipeline should be either type Pipeline or PublishedPipeline")
        if type(pipeline) is Pipeline:
            timenow = datetime.now().strftime('%m-%d-%Y-%H-%M')
            pipeline_name = name + "-" + timenow + "-Pipeline"
            pipeline = pipeline.publish(name=pipeline_name, description="Description for " + pipeline_name)
        pipeline_id = pipeline.id
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        pipeline_endpoint_provider = graph_context.workflow_provider.pipeline_endpoint_provider
        pipeline_endpoint = pipeline_endpoint_provider.create_pipeline_endpoint(name, description, pipeline_id)

        return pipeline_endpoint

    @staticmethod
    def get(workspace, id=None, name=None, _workflow_provider=None, _service_endpoint=None):
        """
        Get the PipelineEndpoint by name or by id, throws exception if either is not provided.

        :param workspace: The workspace the published pipeline was created on.
        :type workspace: azureml.core.Workspace
        :param id: Id of the PipelineEndpoint.
        :type id: str
        :param name: Name of the PipelineEndpoint.
        :type name: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: PipelineEndpoint object
        :rtype: azureml.pipeline.core.PipelineEndpoint
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        pipeline_endpoint_provider = graph_context.workflow_provider.pipeline_endpoint_provider
        result = pipeline_endpoint_provider.get_pipeline_endpoint(id, name)
        return result

    def enable(self):
        """Set the PipelineEndpoint to be 'Active' and available to run."""
        self._set_status('Active')

    def disable(self):
        """Set the PipelineEndpoint to be 'Disabled' and unavailable to run."""
        self._set_status('Disabled')

    def _set_status(self, new_status):
        """Set the PipelineEndpoint status."""
        self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id, status=new_status)
        self._status = new_status

    def get_default_version(self):
        """
        Get the default version of PipelineEndpoint.

        :return: default_version
        :rtype: str
        """
        return self._default_version

    def get_pipeline(self, version=None):
        """
        Get pipeline of given version or default and throws exception if given version not found.

        :return: published pipeline
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        if version is None:
            version = self._default_version
        for pipeline_version in self.pipeline_version_list:
            if pipeline_version.version == version:
                pipeline_id = pipeline_version.pipeline_id

                published_pipeline_provider = self._published_pipeline_provider
                pipeline = published_pipeline_provider.get_published_pipeline(pipeline_id)

                return pipeline

        raise ValueError('Version %s, pipeline not found in pipelineEndpoint %s' % (version, self.id))

    def get_all_versions(self, _workflow_provider=None, _service_endpoint=None):
        """
        Get list of pipelines and corresponding versions in PipelineEndpoint.

        NOTE: This method is being deprecated in favor of list_versions()

        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :return: a list of :class:`azureml.pipeline.core.pipeline_endpoint.PipelineVersion`
        :rtype: :class:`list`
        """
        logging.warning("get_all_versions() is being deprecated. "
                        "Use list_versions() instead.")
        return self.list_versions(_workflow_provider=_workflow_provider, _service_endpoint=_service_endpoint)

    def list_versions(self, _workflow_provider=None, _service_endpoint=None):
        """
        Get list of pipelines and corresponding versions in PipelineEndpoint.

        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :return: a list of :class:`azureml.pipeline.core.pipeline_endpoint.PipelineVersion`
        :rtype: :class:`list`
        """
        published_pipeline_provider = self._published_pipeline_provider
        pipeline_id_list = self._pipeline_version_list
        pipeline_list = [PipelineVersion(pipeline=published_pipeline_provider.get_published_pipeline(
            version_item.pipeline_id), version=version_item.version) for version_item in pipeline_id_list]
        return pipeline_list

    def get_all_pipelines(self, active_only=True, _workflow_provider=None, _service_endpoint=None):
        """
        Get list of pipelines in PipelineEndpoint.

        NOTE: This method is being deprecated in favor of list_pipelines()

        :param active_only: Flag to return active only pipelines.
        :type active_only: bool
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :return: a list of :class:`azureml.pipeline.core.PublishedPipeline`
        :rtype: :class:`list`
        """
        logging.warning("get_all_pipelines() is being deprecated. "
                        "Use list_pipelines() instead.")
        return self.list_pipelines(active_only=active_only, _workflow_provider=_workflow_provider,
                                   _service_endpoint=_service_endpoint)

    def list_pipelines(self, active_only=True, _workflow_provider=None, _service_endpoint=None):
        """
        Get list of pipelines in PipelineEndpoint.

        :param active_only: Flag to return active only pipelines.
        :type active_only: bool
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :return: a list of :class:`azureml.pipeline.core.PublishedPipeline`
        :rtype: :class:`list`
        """
        return self._pipeline_endpoint_provider.get_all_pipelines_from_pipeline_endpoint(
            self.id,
            active_only=active_only)

    @staticmethod
    def get_all(workspace, active_only=True, _workflow_provider=None, _service_endpoint=None):
        """
        Get all active PipelineEndpoints in the current workspace.

        Get all active PipelineEndpoints. NOTE: This method is being deprecated in favor of PipelineEndpoint.list().

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param active_only: If true, only return PipelineEndpoints which are currently active.
        :type active_only: bool
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.PipelineEndpoint`
        :rtype: :class:`list`
        """
        logging.warning("PipelineEndpoint.get_all(workspace) is being deprecated. "
                        "Use PipelineEndpoint.list(workspace) instead.")
        return PipelineEndpoint.list(workspace=workspace, active_only=active_only,
                                     _workflow_provider=_workflow_provider,
                                     _service_endpoint=_service_endpoint)

    @staticmethod
    def list(workspace, active_only=True, _workflow_provider=None, _service_endpoint=None):
        """
        List active PipelineEndpoints in the current workspace.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param active_only: If true, only return PipelineEndpoints which are currently active.
        :type active_only: bool
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.PipelineEndpoint`
        :rtype: :class:`list`
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        pipeline_endpoint_provider = graph_context.workflow_provider.pipeline_endpoint_provider
        return pipeline_endpoint_provider.get_all_pipeline_endpoints(
            active_only=active_only)

    def set_name(self, name):
        """
        Set name of PipelineEndpoint.

        :param name: Name to set.
        :type name: str
        """
        new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id, name=name)
        self._name = new_pipeline_endpoint.name

    def archive(self):
        """Archive PipelineEndpoint."""
        archive_name = str(uuid.uuid4())
        archive_status = 'Disabled'
        new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(
            self.id, name=archive_name, status=archive_status)
        self._name = new_pipeline_endpoint.name
        self._status = new_pipeline_endpoint.status

    def reactivate(self, name):
        """
        Reactivate PipelineEndpoint that have been archived.

        :param name: Name to set.
        :type name: str
        :return: PipelineEndpoint object
        :rtype: azureml.pipeline.core.PipelineEndpoint
        """
        status = 'Active'
        new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id, name=name,
                                                                                          status=status)
        self._name = new_pipeline_endpoint.name
        self._status = new_pipeline_endpoint.status
        return new_pipeline_endpoint

    def add(self, pipeline):
        """
        Add the pipeline to PipelineEndpoint.

        :param pipeline: published pipeline
        :type pipeline: azureml.pipeline.core.graph.PublishedPipeline
        """
        pipeline_id = pipeline.id
        new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id,
                                                                                          pipeline_id=pipeline_id)
        self._pipeline_version_list = new_pipeline_endpoint.pipeline_version_list

    def add_default(self, pipeline):
        """
        Add the pipeline to PipelineEndpoint and set default version to added pipeline version.

        :param pipeline: published pipeline
        :type pipeline: azureml.pipeline.core.graph.PublishedPipeline
        """
        pipeline_id = pipeline.id
        new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id,
                                                                                          pipeline_id=pipeline_id,
                                                                                          add_default=True)
        self._pipeline_version_list = new_pipeline_endpoint.pipeline_version_list
        self._default_version = new_pipeline_endpoint.get_default_version()

    def set_default_version(self, version):
        """
        Set the default version of PipelineEndpoint, throws exception if version not found.

        :param version: version to set for default version in PipelineEndpoint.
        :type version: str
        """
        set_flag = False
        for pipeline_version in self._pipeline_version_list:
            if pipeline_version.version == version:
                set_flag = True
        if set_flag is True:
            new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id,
                                                                                              version=version)
            self._default_version = new_pipeline_endpoint.get_default_version()
        else:
            raise ValueError('Cannot set version %s, does not exist in pipeline endpoint %s. Please, use add()'
                             ' or add_default() to add ' % (version, self.id))

    def set_default(self, pipeline):
        """
        Set the default version of PipelineEndpoint, throws exception if version not found.

        :param pipeline: The publish pipeline
        :type pipeline: azureml.pipeline.core.graph.PublishedPipeline
        """
        set_flag = False
        version = None
        pipeline_id = pipeline.id
        for pipeline_version in self._pipeline_version_list:
            if pipeline_version.pipeline_id == pipeline_id:
                version = pipeline_version.version
                set_flag = True

        if set_flag is True:
            new_pipeline_endpoint = self._pipeline_endpoint_provider.update_pipeline_endpoint(self.id,
                                                                                              version=version)
            self._default_version = new_pipeline_endpoint.get_default_version()
        else:
            raise ValueError('Cannot set pipeline, pipeline id %s does not exist in pipeline endpoint %s.'
                             ' Please, use add() or add_default() to add ' % (pipeline_id, self.id))

    def submit(self, experiment_name, pipeline_parameters=None, parent_run_id=None, pipeline_version=None):
        """
        Submit a pipeline experiment of given version, if version is none triggers default version pipeline.

        :param experiment_name: The name of the experiment to submit the pipeline on.
        :type experiment_name: str
        :param pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
                                    See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        :type pipeline_parameters: dict
        :param parent_run_id: You can supply the run id to set the parent run of this pipeline run.
        :type parent_run_id: str
        :param pipeline_version: The version of pipeline to run
        :type pipeline_version: str

        :return: The submitted pipeline run.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        status = self.status
        if status is not 'Active':
            raise ValueError('Status must be Active, its %s' % status)
        pipeline_run_id = self._pipeline_endpoint_provider.submit_pipeline_run_from_pipeline_endpoint(
            endpoint_id=self.id, experiment_name=experiment_name, parameter_assignment=pipeline_parameters,
            parent_run_id=parent_run_id, pipeline_version=pipeline_version)
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext(experiment_name, self._workspace)
        pipeline_run = PipelineRun(experiment=graph_context._experiment, run_id=pipeline_run_id,
                                   _service_endpoint=graph_context.workflow_provider._service_caller._service_endpoint)
        return pipeline_run

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Description', self.description),
            ('Status', self.status),
            ('Pipelines', self._get_list_info_dict(self.get_all_versions()))
        ])
        return info

    def _get_list_info_dict(self, pipelines):
        list_info = [self._get_pipeline_version_info_dict(version_item) for version_item in pipelines]
        return list_info

    def _get_pipeline_version_info_dict(self, pipeline_version):
        info = OrderedDict([
            ('Version', pipeline_version.version),
            ('Pipeline', self._get_pipeline_info_dict(pipeline_version.pipeline))
        ])
        return info

    @staticmethod
    def _get_pipeline_info_dict(pipeline):
        pipeline_id = make_link(pipeline.get_portal_url(), "endpoint")
        info = OrderedDict([
            ('endpoint', pipeline_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the PipelineEndpoints."""
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Description', self.description),
            ('Pipelines', [(version_pipeline.version, version_pipeline.pipeline)
                           for version_pipeline in self.get_all_versions()])
        ])
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "PipelineEndpoint({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the PipelineEndpoint."""
        return self.__str__()


class PipelineVersion(object):
    """
    A PipelineVersion defines the version, pipeline of a pipelines.

    :param version: The version of pipeline
    :type version: str
    :param pipeline: The PublishedPipeline object
    :type pipeline: azureml.pipeline.core.graph.PublishedPipeline
    """

    def __init__(self, version, pipeline):
        """
        Initialize PipelineVersion.

        :param version: The version of the pipeline.
        :type version: str
        :param pipeline: The published pipeline.
        :type pipeline: azureml.pipeline.core.graph.PublishedPipeline
        """
        self._version = version
        self._pipeline = pipeline

    @property
    def version(self):
        """
        Version of the PipelineVersion.

        :return: The version of pipeline.
        :rtype: str
        """
        return self._version

    @property
    def pipeline(self):
        """
        Pipeline of the PipelineVersion.

        :return: The published pipeline.
        :rtype: azureml.pipeline.core.graph.PublishedPipeline
        """
        return self._pipeline

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        pipeline_id = make_link(self.pipeline.get_portal_url(), self.pipeline.id)
        info = OrderedDict([
            ('version', self.version),
            ('pipeline', pipeline_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the PipelineVersion."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "PipelineVersion({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the PipelineVersion."""
        return self.__str__()


class PipelineIdVersion(object):
    """A PipelineIdVersion defines the version, pipeline id of a pipeline."""

    def __init__(self, version, pipeline_id):
        """
        Initialize PipelineIdVersion.

        :param version: The version of the pipeline.
        :type version: str
        :param pipeline_id: The published pipeline id.
        :type pipeline: str
        """
        self._version = version
        self._pipeline_id = pipeline_id

    @property
    def version(self):
        """
        Version of the PipelineVersion.

        :return: The version of pipeline.
        :rtype: str
        """
        return self._version

    @property
    def pipeline_id(self):
        """
        Id of the Pipeline.

        :return: The id of pipeline.
        :rtype: str
        """
        return self._pipeline_id

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('Version', self.version),
            ('PipelineId', self.pipeline_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the PipelineIdVersion."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "PipelineIdVersion({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the PipelineIdVersion."""
        return self.__str__()
