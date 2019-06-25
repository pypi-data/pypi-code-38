# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Windows executable in Azure Batch."""
from azureml.core.compute import BatchCompute
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _FolderModuleBuilder, _InterfaceModuleBuilder

import re


class AzureBatchStep(PipelineStep):
    """
    PipelineStep class for submitting jobs to AzureBatch.

    See example of using this step in notebook https://aka.ms/pl-azbatch

    :param name: Name of the step (mandatory)
    :type name: str
    :param create_pool: Boolean flag to indicate whether create the pool before running the jobs
    :type create_pool: bool
    :param delete_batch_job_after_finish: Boolean flag to indicate whether to delete the job from
                                        Batch account after it's finished
    :type delete_batch_job_after_finish: bool
    :param delete_batch_pool_after_finish: Boolean flag to indicate whether to delete the pool after
                                        the job finishes
    :type delete_batch_pool_after_finish: bool
    :param is_positive_exit_code_failure: Boolean flag to indicate if the job fails if the task exists
                                        with a positive code
    :type is_positive_exit_code_failure: bool
    :param vm_image_urn: If create_pool is true and VM uses VirtualMachineConfiguration.
                         Value format: ``urn:publisher:offer:sku``.
                         Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``
    :type vm_image_urn: str
    :param pool_id: (Mandatory) The Id of the Pool where the job will run
    :type pool_id: str
    :param run_task_as_admin: Boolean flag to indicate if the task should run with Admin privileges
    :type run_task_as_admin: bool
    :param target_compute_nodes: Assumes create_pool is true, indicates how many compute nodes will be added
                                to the pool
    :type target_compute_nodes: int
    :param source_directory: Local folder that contains the module binaries, executable, assemblies etc.
    :type source_directory: str
    :param executable: Name of the command/executable that will be executed as part of the job
    :type executable: str
    :param arguments: Arguments for the command/executable
    :type arguments: str
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                    azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param vm_size: If create_pool is true, indicating Virtual machine size of the compute nodes
    :type vm_size: str
    :param compute_target: BatchCompute compute
    :type compute_target: BatchCompute, str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the module
    :type version: str
    """

    def __init__(self,
                 name,
                 create_pool=False,
                 pool_id=None,
                 delete_batch_job_after_finish=False,
                 delete_batch_pool_after_finish=False,
                 is_positive_exit_code_failure=True,
                 vm_image_urn="urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter",
                 run_task_as_admin=False,
                 target_compute_nodes=1,
                 vm_size="standard_d1_v2",
                 source_directory=None,
                 executable=None,
                 arguments=None,
                 inputs=None,
                 outputs=None,
                 allow_reuse=True,
                 compute_target=None,
                 version=None):
        """
        Pipelinestep class for submitting jobs to AzureBatch.

        :param name: Name of the step (mandatory)
        :type name: str
        :param create_pool: Boolean flag to indicate whether create the pool before running the jobs
        :type create_pool: bool
        :param delete_batch_job_after_finish: Boolean flag to indicate whether to delete the job from
                                            Batch account after it's finished
        :type delete_batch_job_after_finish: bool
        :param delete_batch_pool_after_finish: Boolean flag to indicate whether to delete the pool after
                                            the job finishes
        :type delete_batch_pool_after_finish: bool
        :param is_positive_exit_code_failure: Boolean flag to indicate if the job fails if the task exists
                                            with a positive code
        :type is_positive_exit_code_failure: bool
        :param vm_image_urn: If create_pool is true and VM uses VirtualMachineConfiguration.
                             Value format: ``urn:publisher:offer:sku``.
                             Example: ``urn:MicrosoftWindowsServer:WindowsServer:2012-R2-Datacenter``
        :type vm_image_urn: str
        :param pool_id: (Mandatory) The Id of the Pool where the job will run
        :type pool_id: str
        :param run_task_as_admin: Boolean flag to indicate if the task should run with Admin privileges
        :type run_task_as_admin: bool
        :param target_compute_nodes: Assumes create_pool is true, indicates how many compute nodes will be added
                                    to the pool
        :type target_compute_nodes: int
        :param source_directory: Local folder that contains the module binaries, executable, assemblies etc.
        :type source_directory: str
        :param executable: Name of the command/executable that will be executed as part of the job
        :type executable: str
        :param arguments: Arguments for the command/executable
        :type arguments: list
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                        azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                        azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                        azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param vm_size: If create_pool is true, indicating Virtual machine size of the compute nodes
        :type vm_size: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the module
        :type version: str
        """
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')

        if compute_target is None:
            raise ValueError('compute_target is required')
        self._compute_target = compute_target

        self._source_directory = source_directory

        self._metadata_parameters = dict()

        self._optional_parameters = dict()
        self._optional_parameters["RunTaskAsAdmin"] = run_task_as_admin
        self._optional_parameters["IsPositiveExitCodeFailure"] = is_positive_exit_code_failure
        self._optional_parameters["DeleteBatchPoolAfterFinish"] = delete_batch_pool_after_finish
        self._optional_parameters["DeleteBatchJobAfterFinish"] = delete_batch_job_after_finish
        self._optional_parameters["TargetComputeNodes"] = target_compute_nodes
        self._optional_parameters["CreatePool"] = create_pool
        self._optional_parameters["VmSize"] = vm_size

        self._parameters = dict()
        self._parameters["PoolId"] = pool_id
        if executable is None:
            raise ValueError('executable is required')
        self._parameters["Executable"] = executable

        self.__populate_vm_image_params_from_urn(urn=vm_image_urn)

        self._inputs = inputs
        self._outputs = outputs

        PipelineStep._process_pipeline_io(arguments, self._inputs, self._outputs)

        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(arguments)
        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(
            params=self._parameters)
        self._pipeline_params_in_step_params.update(PipelineStep._get_pipeline_parameters_step_params(
            params=self._optional_parameters))

        self._allow_reuse = allow_reuse
        self._version = version

        super(AzureBatchStep, self).__init__(name, self._inputs, self._outputs, arguments)

    def __populate_vm_image_params_from_urn(self, urn):
        tokens = urn.split(':')
        if len(tokens) < 4 or tokens[0] != "urn":
            raise TypeError("urn format is incorrect, expected format: 'urn:publisher:offer:sku'")
        self._optional_parameters["ImagePublisher"] = tokens[1]
        self._optional_parameters["ImageOffer"] = tokens[2]
        self._optional_parameters["ImageSkuKeyword"] = tokens[3]

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from the AzureBatch step and adds it to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: The default datastore.
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs,
                                                                            self._outputs,
                                                                            default_datastore)

        AzureBatchStep.add_metadata_params(context, self._compute_target, self._metadata_parameters)

        arguments = super(AzureBatchStep, self).resolve_input_arguments(
            self._arguments, self._inputs, self._outputs, list(self._parameters))
        if arguments is not None and len(arguments) > 0:
            self._parameters['Arguments'] = ",".join([str(x) for x in arguments])

        param_defs = [ParamDef(param) for param in self._parameters]
        param_defs += [ParamDef(param, is_optional=True) for param in self._optional_parameters]
        param_defs += [ParamDef(param, is_metadata_param=True) for param in self._metadata_parameters]

        module_def = self.create_module_def(execution_type="AzureBatchCloud",
                                            input_bindings=input_bindings,
                                            output_bindings=output_bindings,
                                            param_defs=param_defs,
                                            allow_reuse=self._allow_reuse,
                                            version=self._version)

        if self._source_directory is None:
            module_builder = _InterfaceModuleBuilder(context=context,
                                                     module_def=module_def)
        else:
            module_builder = _FolderModuleBuilder(
                content_root=self._source_directory,
                hash_paths=[self._source_directory],
                context=context,
                module_def=module_def)

        param_values = self._parameters
        param_values.update(self._metadata_parameters)

        node = graph.add_module_node(name=self.name,
                                     input_bindings=input_bindings,
                                     output_bindings=output_bindings,
                                     param_bindings=param_values,
                                     module_builder=module_builder)

        PipelineStep. \
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_implicit=self._pipeline_params_implicit,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params)
        return node

    @staticmethod
    def add_metadata_params(context, compute_target, metadata_params):
        """
        Add metadata params to metadata params dictionary.

        :param context: The graph context object
        :type context: _GraphContext
        :param compute_target: BatchCompute compute
        :type compute_target: BatchCompute, str
        :param metadata_params: Dictionary of name-value pairs
        :type metadata_params: {str: str}
        """
        azurebatch_config = AzureBatchStep._get_azurebatch_config(context, compute_target)
        metadata_params.update(azurebatch_config)

    @staticmethod
    def _get_azurebatch_config(context, compute_target):
        """
        Get the AzureBatch config.

        :param context: context
        :type context: _GraphContext
        :param compute_target: BatchCompute compute
        :type compute_target: BatchCompute, str

        :return: The AzureBatch config.
        :rtype: dict
        """
        azurebatch_resource_id = AzureBatchStep._get_azurebatch_resource_id(context, compute_target)
        resource_id_regex = \
            r'\/subscriptions\/([^/]+)\/resourceGroups\/([^/]+)\/providers\/Microsoft\.Batch\/batchAccounts\/([^/]+)'

        match = re.search(resource_id_regex, azurebatch_resource_id, re.IGNORECASE)

        if match is None:
            raise ValueError('AzureBatch resource Id format is incorrect: {0}, the correct format is: {1}'
                             .format(azurebatch_resource_id, "/subscriptions/{SubscriptionId}/"
                                                             "resourceGroups/{ResourceGroup}/"
                                                             "providers/Microsoft.Batch/batchAccounts/{BatchAccount}"))
        return {
            'SubscriptionId': match.group(1),
            'ResourceGroup': match.group(2),
            'AccountName': match.group(3)
        }

    @staticmethod
    def _get_azurebatch_resource_id(context, compute_target):
        """
        Get the AzureBatch resource id.

        :param context: context
        :type context: _GraphContext
        :param compute_target: BatchCompute compute
        :type compute_target: BatchCompute, str

        :return: The AzureBatch resource id.
        :rtype: str
        """
        if isinstance(compute_target, BatchCompute):
            return compute_target.cluster_resource_id

        if isinstance(compute_target, str):
            try:
                compute_target = BatchCompute(context._workspace, compute_target)
                return compute_target.cluster_resource_id
            except Exception as e:
                raise ValueError('Error in getting AzureBatch compute: {}'.format(e))

        raise ValueError('compute_target is not specified correctly')
