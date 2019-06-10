# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""pipeline.py, module for creating and submitting a pipeline."""
from azureml.pipeline.core._graph_context import _GraphContext
from azureml.pipeline.core.builder import _PipelineGraphBuilder
from azureml.core._experiment_method import experiment_method


def _submit_pipeline(pipeline, workspace, experiment_name, **kwargs):
    """
    Submit a pipeline.

    :param pipeline: pipeline
    :type pipeline: Pipeline
    :param workspace: workspace
    :type workspace: Workspace
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    continue_on_step_failure = False
    regenerate_outputs = False
    pipeline_params = None
    parent_run_id = None
    for key, value in kwargs.items():
        if key == 'continue_on_step_failure':
            continue_on_step_failure = value
        elif key == 'regenerate_outputs':
            regenerate_outputs = value
        elif key == 'pipeline_params':
            pipeline_params = value
        elif key == 'parent_run_id':
            parent_run_id = value

    return pipeline.submit(experiment_name, pipeline_parameters=pipeline_params,
                           continue_on_step_failure=continue_on_step_failure,
                           regenerate_outputs=regenerate_outputs, parent_run_id=parent_run_id)


class Pipeline(object):
    """
    A Pipeline represents a collection of steps which can be executed as a workflow.

    Use a Pipeline to create and manage workflows that stitch together various machine learning
    phases. Each machine learning phase, such as data preparation and model training, can consist of one or
    more steps in a Pipeline.

    See the following link for an overview on constructing a Pipeline: `https://aka.ms/pl-first-pipeline`

    .. remarks::

        A pipeline is created with a list of steps and a workspace.

        There are a number of Step types which can be used in a Pipeline. Each Step type provides particular
        functionality for various machine learning scenarios.

        The types of Steps which can be used in a Pipeline are:

        *  :class:`azureml.pipeline.steps.AdlaStep`
        *  :class:`azureml.train.automl.AutoMLStep`
        *  :class:`azureml.pipeline.steps.AzureBatchStep`
        *  :class:`azureml.pipeline.steps.DatabricksStep`
        *  :class:`azureml.pipeline.steps.DataTransferStep`
        *  :class:`azureml.pipeline.steps.EstimatorStep`
        *  :class:`azureml.pipeline.steps.HyperDriveStep`
        *  :class:`azureml.pipeline.steps.MpiStep`
        *  :class:`azureml.pipeline.steps.PythonScriptStep`

        Submit a pipeline using :func:`azureml.core.Experiment.submit`. When submit is called,
        a :class:`azureml.pipeline.core.PipelineRun` is created which in turn creates
        :class:`azureml.pipeline.core.StepRun` objects for each step in the workflow. Use these objects to monitor
        the run execution.

        An example to submit a Pipeline is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            pipeline_run = experiment.submit(pipeline)

        There are a number of optional settings for a Pipeline which can be specified at submission time.
        These include:

        *  continue_on_step_failure: Whether to continue pipeline execution if a step fails, default is False.
        *  regenerate_outputs: Whether to force regeneration of all step outputs and disallow data reuse for
            this run, default is False.
        *  pipeline_params: Parameters to pipeline execution, dictionary of {name: value}.
                            See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        *  parent_run_id: You can supply the run id to set the parent run of this pipeline run.

        An example to submit a Pipeline using these settings is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            pipeline_run = experiment.submit(pipeline,
                                             continue_on_step_failure=True,
                                             regenerate_outputs=True,
                                             pipeline_params={"param1": "value1"},
                                             parent_run_id="<run_id>")


    :param workspace: The workspace to submit the Pipeline on.
    :type workspace: azureml.core.workspace.Workspace
    :param steps: The list steps to execute as part of a Pipeline.
    :type steps: :class:`list`
    :param description: The description of the Pipeline.
    :type description: str
    :param default_datastore: The default datastore to use for data connections.
    :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
    :param default_source_directory: The default script directory for steps which execute a script.
    :type default_source_directory: str
    :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
    :type resolve_closure: bool
    """

    @experiment_method(submit_function=_submit_pipeline)
    def __init__(self, workspace, steps, description=None,
                 default_datastore=None, default_source_directory=None, resolve_closure=True,
                 _workflow_provider=None, _service_endpoint=None):
        """
        Initialize Pipeline.

        :param workspace: The workspace to submit the Pipeline on.
        :type workspace: azureml.core.workspace.Workspace
        :param steps: The list steps to execute as part of a Pipeline.
        :type steps: :class:`list`
        :param description: The description of the Pipeline.
        :type description: str
        :param default_datastore: The default datastore to use for data connections.
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param default_source_directory: The default script directory for steps which execute a script.
        :type default_source_directory: str
        :param resolve_closure: Whether resolve closure or not (automatically bring in dependent steps).
        :type resolve_closure: bool
        :param _workflow_provider: The workflow provider, if None one is created.
        :type _workflow_provider: azureml.pipeline.core._aeva_provider._AevaWorkflowProvider
        :param _service_endpoint: The service endpoint, if None it is determined using the workspace.
        :type _service_endpoint: str
        """
        self._name = description

        self._graph_context = _GraphContext("placeholder", workspace=workspace,
                                            default_source_directory=default_source_directory,
                                            workflow_provider=_workflow_provider,
                                            service_endpoint=_service_endpoint)
        self._graph_builder = _PipelineGraphBuilder(resolve_closure=resolve_closure,
                                                    context=self._graph_context,
                                                    default_datastore=default_datastore)
        if 'aether-dev' in self._graph_context.service_endpoint:
            print('Using dev endpoint:', self._graph_context.service_endpoint)

        self._graph = self._graph_builder.build(self._name, steps, finalize=False)

    def _set_experiment_name(self, name):
        self._graph_context.experiment_name = name
        if self._graph._name is None:
            self._graph._name = name
        if self._name is None:
            self._name = name

    @property
    def graph(self):
        """
        Get the graph associated with the pipeline. Steps and data inputs appear as nodes in the graph.

        :return: The graph.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        return self._graph

    def validate(self):
        """
        Validate a pipeline and identify potential errors, such as unconnected inputs.

        :return: A list of errors in the pipeline.
        :rtype: :class:`list`
        """
        return self.graph.validate()

    def _finalize(self, regenerate_outputs=False):
        """
        Finalize the graph.

        :param regenerate_outputs: Whether to regenerate step outputs.
        :type regenerate_outputs: bool

        :return: Dictionary of {node_id, (resource_id, is_new_resource)}
        :rtype: dict
        """
        return self.graph.finalize(regenerate_outputs=regenerate_outputs)

    def submit(self, experiment_name, pipeline_parameters=None, continue_on_step_failure=False,
               regenerate_outputs=False, parent_run_id=None):
        """
        Submit a pipeline run. This is equivalent to using :func:`azureml.core.Experiment.submit`.

        Returns the submitted :class:`azureml.pipeline.core.PipelineRun`. Use this object to monitor and
        view details of the run.

        :param experiment_name: The name of the experiment to submit the pipeline on.
        :type experiment_name: str
        :param pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
                                    See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        :type pipeline_parameters: dict
        :param continue_on_step_failure: Whether to continue pipeline execution if a step fails.
        :type continue_on_step_failure: bool
        :param regenerate_outputs: Whether to force regeneration of all step outputs and disallow data reuse for
            this run. If False, this run may reuse results from previous runs and subsequent runs may reuse
            the results of this run.
        :type regenerate_outputs: bool
        :param parent_run_id: You can supply the run id to set the parent run of this pipeline run.
        :type parent_run_id: str

        :return: The submitted pipeline run.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        self._set_experiment_name(experiment_name)

        return self.graph.submit(pipeline_parameters=pipeline_parameters,
                                 continue_on_step_failure=continue_on_step_failure,
                                 regenerate_outputs=regenerate_outputs,
                                 parent_run_id=parent_run_id)

    def publish(self, name=None, description=None, version=None, continue_on_step_failure=None):
        """
        Publish a pipeline and make it available for rerunning.

        Once a Pipeline is published, it can be submitted without the Python code which constructed
        the Pipeline. Returns the created :class:`azureml.pipeline.core.PublishedPipeline`.

        :param name: Name of the published pipeline.
        :type name: str
        :param description: Description of the published pipeline.
        :type description: str
        :param version: Version of the published pipeline.
        :type version: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                         if a step fails, default is false.
        :type continue_on_step_failure: bool

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        return self.graph._save(name=name, description=description, version=version,
                                continue_on_step_failure=continue_on_step_failure)
