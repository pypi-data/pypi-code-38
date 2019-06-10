# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run an Estimator as part of the Machine Learning model training."""
from azureml.pipeline.steps import PythonScriptStep


class EstimatorStep(PythonScriptStep):
    """Adds a step to run Estimator in a Pipeline.

    Note: The arguments to the entry script used in the Estimator object should be specified as *list* using
    'estimator_entry_script_arguments' parameter when instantiating EstimatorStep. Estimator object's parameter
    'script_params' accepts a dictionary. However 'estimator_entry_script_arguments' parameter expects arguments as
    a list.

    Estimator object initialization involves specifying a list of DataReference objects in its 'inputs' parameter.
    In Pipelines, a step can take another step's output or DataReferences as input. So when creating an EstimatorStep,
    the parameters 'inputs' and 'outputs' need to be set explicitly and that will override 'inputs' parameter
    specified in the Estimator object.

    See example of using this step in notebook https://aka.ms/pl-estimator

    :param name: name
    :type name: str
    :param estimator: estimator object
    :type estimator: azureml.train.estimator.Estimator
    :param estimator_entry_script_arguments: List of command-line arguments
    :type estimator_entry_script_arguments: [str]
    :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                    name of the runconfig property and PipelineParameter for that property
    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param inputs: inputs
    :type inputs: list[azureml.pipeline.core.builder.PipelineData, azureml.data.data_reference.DataReference,
                    azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.PipelineDataset]
    :param outputs: output is list of PipelineData
    :type outputs: list[azureml.pipeline.core.builder.PipelineData]
    :param compute_target: Compute target to use
    :type compute_target: azureml.core.compute.DsvmCompute, azureml.core.compute.AmlCompute,
        azureml.core.compute.RemoteTarget, str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: version
    :type version: str
    """

    def __init__(self, name=None, estimator=None, estimator_entry_script_arguments=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None,
                 compute_target=None, allow_reuse=True, version=None):
        """
        Initialize EstimatorStep.

        :param name: name
        :type name: str
        :param estimator: estimator
        :type estimator: Estimator
        :param estimator_entry_script_arguments: List of command-line arguments
        :type estimator_entry_script_arguments: [str]
        :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                        name of the runconfig property and PipelineParameter for that property
        :type runconfig_pipeline_params: {str: PipelineParameter}
        :param inputs: inputs
        :type inputs: list[azureml.pipeline.core.builder.PipelineData, azureml.data.data_reference.DataReference,
                        azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                        azureml.pipeline.core.PipelineDataset]
        :param outputs: outputs
        :type outputs: list[azureml.pipeline.core.builder.PipelineData]
        :param compute_target: Compute target to use
        :type compute_target: azureml.core.compute.DsvmCompute, azureml.core.compute.AmlCompute,
            azureml.core.compute.RemoteTarget, str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: version
        :type version: str
        """
        # the following args are required
        if None in [estimator, compute_target]:
            raise ValueError("Estimator, compute_target parameters are required")

        if estimator_entry_script_arguments is None:
            raise ValueError('estimator_entry_script_arguments is a required parameter. If the Estimator''s entry'
                             'script does not accept commandline arguments, set the parameter value to empty list')

        from azureml.train.estimator import MMLBaseEstimator
        if not isinstance(estimator, MMLBaseEstimator):
            raise Exception("Estimator parameter is not of valid type")

        # resetting compute_target, arguments and data refs as they will not be used in EstimatorStep
        estimator.run_config._target = None
        estimator.run_config.arguments = []
        estimator.run_config.data_references = []

        run_config = estimator.run_config
        source_directory = estimator.source_directory
        script_name = run_config.script

        super(EstimatorStep, self).__init__(name=name, script_name=script_name,
                                            arguments=estimator_entry_script_arguments, compute_target=compute_target,
                                            runconfig=run_config, runconfig_pipeline_params=runconfig_pipeline_params,
                                            inputs=inputs, outputs=outputs,
                                            source_directory=source_directory, allow_reuse=allow_reuse,
                                            version=version)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: context
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(EstimatorStep, self).create_node(graph, default_datastore, context)
