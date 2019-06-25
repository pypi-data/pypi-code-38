# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to use an existing version of a Module."""
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core._python_script_step_base import _PythonScriptStepBase
from azureml.pipeline.core.graph import Module as GraphModule
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider


class ModuleStep(PipelineStep):
    """Adds a step that uses a specific module.

    A ModuleStep is a node in pipeline that uses an existing Module, and specifically, one of its versions.
    In order to define which ModuleVersion would eventually be used in the submitted pipeline, the user can define
    one of the following when creating the ModuleStep:
    -   ModuleVersion object
    -   Module object and a version value
    -   Only Module without a version value, in this case the resolution is to use may vary across submissions.

    The user also needs to define the mapping between the step's inputs and outputs to the ModuleVersion's inputs
    and outputs.

    :param module: Module of the step
    :type module: azureml.pipeline.core.Module
    :param version: version of the module
    :type version: str
    :param module_version: ModuleVersion of the step. Either Module of ModuleVersion must be provided
    :type module_version: azureml.pipeline.core.ModuleVersion
    :param inputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
    :type inputs_map: {str: azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset}
    :param outputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
    :type outputs_map: {str: azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset}
    :param runconfig_pipeline_params: Override runconfig properties at runtime using key-value pairs each with
                                    name of the runconfig property and PipelineParameter for that property
    :type runconfig_pipeline_params: {str: PipelineParameter}
    :param arguments: Command line arguments for the python script file. The arguments will be delivered
                      to compute via arguments in RunConfiguration.
                      For more details how to handle arguments such as special symbols, please refer
                      arguments in :class:`azureml.core.RunConfiguration`
    :type arguments: [str]
    :param params: Dictionary of name-value pairs
    :type params: {str: str}
    """

    def __init__(self, module=None, version=None, module_version=None,
                 inputs_map=None, outputs_map=None,
                 compute_target=None, runconfig=None,
                 runconfig_pipeline_params=None, arguments=None, params=None,
                 _workflow_provider=None):
        """
        Initialize ModuleStep.

        :param module: Module of the step
        :type module: azureml.pipeline.core.Module
        :param version: version of the module
        :type version: str
        :param module_version: ModuleVersion of the step. Either Module of ModuleVersion must be provided
        :type module_version: azureml.pipeline.core.ModuleVersion
        :param inputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
        :type inputs_map: {str:
                      azureml.pipeline.core.graph.InputPortBinding,azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                      azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                      azureml.pipeline.core.PipelineDataset}
        :param outputs_map: Dictionary, keys are names of inputs on the module_version, values are input port bindings
        :type outputs_map: {str:
                      azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                      azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                      azureml.pipeline.core.PipelineDataset}
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
        :param arguments: Command line arguments for the python script file. The arguments will be delivered
                          to compute via arguments in RunConfiguration.
                          For more details how to handle arguments such as special symbols, please refer
                          arguments in :class:`azureml.core.RunConfiguration`
        :type arguments: [str]
        :param params: Dictionary of name-value pairs
        :type params: {str: str}
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        """
        _workflow_provider = _workflow_provider
        if outputs_map is None:
            outputs_map = {}
        if inputs_map is None:
            inputs_map = {}
        if params is None:
            params = {}
        if module is None and module_version is None:
            raise ValueError('Exactly one of module or module_version is required but both are missing')
        if module is not None and module_version is not None:
            raise ValueError('Exactly one of module or module_version is required but both are provided')

        self._params = params
        self._runconfig_pipeline_params = runconfig_pipeline_params

        if compute_target is None and runconfig is not None:
            self._compute_target = runconfig.target
        else:
            self._compute_target = compute_target
        self._runconfig = runconfig
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(arguments=arguments)
        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(params)
        PipelineStep._validate_params(self._params, self._runconfig_pipeline_params)
        self._pipeline_params_runconfig = PipelineStep._get_pipeline_parameters_runconfig(runconfig_pipeline_params)

        self._update_param_bindings()

        name = ""
        if module_version is not None:
            name = module_version.module(_workflow_provider=_workflow_provider).name
            self._module_version = module_version
            self._version = module_version.version
        else:
            name = module.name
            self._module = module
            self._version = version
            self._module_version = None
        self._module_wiring = {"inputs": inputs_map, "outputs": outputs_map}
        keys = inputs_map.keys()
        for key in keys:
            if isinstance(inputs_map[key], tuple):
                inputs_map[key] = PipelineStep._tuple_to_ioref(inputs_map[key])
        keys = outputs_map.keys()
        for key in keys:
            if isinstance(outputs_map[key], tuple):
                outputs_map[key] = PipelineStep._tuple_to_ioref(outputs_map[key])

        PipelineStep._process_pipeline_io(arguments, None, None)
        inputs = list(inputs_map.values())
        outputs = list(outputs_map.values())
        super(self.__class__, self).__init__(name, inputs, outputs)

    # automatically add pipeline params to param binding
    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                # example: if the user specifies a non-pipeline param and a pipeline param with same name
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))

    def create_node(self, graph, default_datastore, context):
        """
        Create a node.

        :param graph: graph object
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: context
        :type context: _GraphContext

        :return: The node object.
        :rtype: azureml.pipeline.core.graph.Node
        """
        if self._module_version is None:
            self._module_version = self._module.resolve(self._version)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        # repopulating the wiring with the processed bindings
        output_bindings_dict = {}
        for ob in output_bindings:
            output_bindings_dict[ob.name] = ob

        input_bindings_dict = {}
        for ib in input_bindings:
            input_bindings_dict[ib.name] = ib

        output_wiring = {}
        for wiring_target in self._module_wiring["outputs"].keys():
            output_name = self._module_wiring["outputs"][wiring_target].name
            processed_output = output_bindings_dict[output_name]
            output_wiring[wiring_target] = processed_output

        input_wiring = {}
        for wiring_target in self._module_wiring["inputs"].keys():
            input_name = self._module_wiring["inputs"][wiring_target].name
            processed_input = input_bindings_dict[input_name]
            input_wiring[wiring_target] = processed_input

        self._module_wiring["inputs"] = input_wiring
        self._module_wiring["outputs"] = output_wiring

        graph_module = GraphModule(module_id=self._module_version.module_version_id,
                                   module_version=self._module_version, default_version=self._version)
        node = graph.add_module_node(self.name, input_bindings, output_bindings, self._params,
                                     module=graph_module, module_wiring=self._module_wiring)

        PipelineStep.\
            _configure_pipeline_parameters(graph,
                                           node,
                                           pipeline_params_implicit=self._pipeline_params_implicit,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params,
                                           pipeline_params_runconfig=self._pipeline_params_runconfig)

        if self._runconfig is not None:
            self._set_compute_params_to_node(node, context)

        return node

    def _set_compute_params_to_node(self, node, context):
        """Compute params.

        :param node: node object
        :type node: Node
        :param context: context
        :type context: _GraphContext
        """
        compute_target_name, compute_target_type, compute_target_object = _PythonScriptStepBase. \
            _extract_compute_target_params(context, self._compute_target)
        runconfig_params = _PythonScriptStepBase._prepare_runconfig(self._runconfig)

        arguments = super(ModuleStep, self).resolve_input_arguments(
            self._arguments, self._inputs, self._outputs, self._params)
        _ModuleParameterProvider().set_params_to_node(
            node=node, target_name=compute_target_name, target_type=compute_target_type,
            target_object=compute_target_object, script_name=None, arguments=arguments,
            runconfig_params=runconfig_params, batchai_params={})
