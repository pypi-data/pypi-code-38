# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Python script."""
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase


class PythonScriptStep(_PythonScriptStepBase):
    r"""Add a step to run a Python script in a Pipeline.

    See example of using this step in notebook https://aka.ms/pl-get-started

    :param script_name: Name of a python script (relative to source_directory).
    :type script_name: str
    :param name: Name of the step. If unspecified, script_name will be used
    :type name: str
    :param arguments: Command line arguments for the python script file. The arguments will be delivered
                      to compute via arguments in RunConfiguration.
                      For more details how to handle arguments such as special symbols, please refer
                      arguments in :class:`azureml.core.RunConfiguration`
    :type arguments: list
    :param compute_target: Compute target to use.  If unspecified, the target from the runconfig will be used.
        compute_target may be a compute target object or the string name of a compute target on the workspace.
        Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
        ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
        type is 'AmlCompute' and RemoteTarget type is 'VirtualMachine')
    :type compute_target: DsvmCompute, AmlCompute, RemoteTarget, HDIClusterTarget, str, tuple
    :param runconfig: The RunConfiguration to use, optional. A RunConfiguration can be used to specify additional
                      requirements for the run, such as conda dependencies and a docker image.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                    name of the runconfig property and PipelineParameter for that property
    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
        azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
        azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
        azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param params: Dictionary of name-value pairs. Registered as environment variables with "AML_PARAMETER\_"
    :type params: dict
    :param source_directory: Folder that contains the script, conda env etc.
    :type source_directory: str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step
    :type version: str
    :param hash_paths: List of paths to hash when checking for changes to the step contents.  If there
        are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
        contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
        (DEPRECATED), no longer needed.
    :type hash_paths: list
    """

    def __init__(self, script_name, name=None, arguments=None, compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, inputs=None, outputs=None, params=None, source_directory=None,
                 allow_reuse=True, version=None, hash_paths=None):
        """
        Add a step to run a Python script in a Pipeline.

        :param script_name: Name of a python script (relative to source_directory)
        :type script_name: str
        :param name: Name of the step.  If unspecified, script_name will be used
        :type name: str
        :param arguments: Command line arguments for the python script file. The arguments will be delivered
                          to compute via arguments in RunConfiguration.
                          For more details how to handle arguments such as special symbols, please refer
                          arguments in :class:`azureml.core.RunConfiguration`
        :type arguments: [str]
        :param compute_target: Compute target to use.  If unspecified, the target from the runconfig will be used.
            Compute_target may be a compute target object or the string name of a compute target on the workspace.
            Optionally if the compute target is not available at pipeline creation time, you may specify a tuple of
            ('compute target name', 'compute target type') to avoid fetching the compute target object (AmlCompute
            type is 'AmlCompute' and RemoteTarget type is 'VirtualMachine')
        :type compute_target: DsvmCompute, AmlCompute, RemoteTarget, HDIClusterTarget, str, tuple
        :param runconfig: The RunConfiguration to use. RunConfiguration can be used to specify additional requirements
                          for the run, such as conda dependencies and a docker image. If unspecified, a
                          default runconfig will be created
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                        name of the runconfig property and PipelineParameter for that property
        :type runconfig_pipeline_params: {str: PipelineParameter}
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                     azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                     azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                     azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param params: Dictionary of name-value pairs. Registered as environment variables with "AML_PARAMETER_"
        :type params: {str: str}
        :param source_directory: folder that contains the script, conda env etc.
        :type source_directory: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the step
        :type version: str
        :param hash_paths: List of paths to hash when checking for changes to the step contents.  If there
            are no changes detected, the pipeline will reuse the step contents from a previous run. By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            (DEPRECATED), no longer needed.
        :type hash_paths: list
        """
        super(PythonScriptStep, self).__init__(
            script_name=script_name, name=name, arguments=arguments, compute_target=compute_target,
            runconfig=runconfig, runconfig_pipeline_params=runconfig_pipeline_params, inputs=inputs, outputs=outputs,
            params=params, source_directory=source_directory, allow_reuse=allow_reuse, version=version,
            hash_paths=hash_paths)

    def create_node(self, graph, default_datastore, context):
        """
        Create a node for python script step.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: context
        :type context: _GraphContext

        :return: The created node
        :rtype: azureml.pipeline.core.graph.Node
        """
        return super(PythonScriptStep, self).create_node(
            graph=graph, default_datastore=default_datastore, context=context)

    def set_amlcompute_params(self, native_shared_directory=None):
        """
        Set AmlCompute native shared directory param.

        :param native_shared_directory: native shared directory
        :type native_shared_directory: str
        """
        super(PythonScriptStep, self).set_amlcompute_params(native_shared_directory=native_shared_directory)
