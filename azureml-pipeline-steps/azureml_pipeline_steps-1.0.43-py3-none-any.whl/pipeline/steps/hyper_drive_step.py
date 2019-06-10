# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Hyper Parameter tuning as part of the Machine Learning model training."""
import json
import logging
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineStep, PipelineData
from azureml.pipeline.core._module_builder import _InterfaceModuleBuilder
from azureml.pipeline.core.graph import ParamDef, OutputPortBinding
from azureml.train.hyperdrive.run import HyperDriveRun


module_logger = logging.getLogger(__name__)


class HyperDriveStep(PipelineStep):
    """Creates a HyperDrive step in a Pipeline.

    Note: The arguments to the entry script used in the Estimator object should be specified as *list* using
    'estimator_entry_script_arguments' parameter when instantiating HyperDriveStep. Estimator object's parameter
    'script_params' accepts a dictionary. However 'estimator_entry_script_arguments' parameter expects arguments as
    a list.

    Estimator object initialization involves specifying a list of DataReference objects in its 'inputs' parameter.
    In Pipelines, a step can take another step's output or DataReferences as input. So when creating an HyperDriveStep,
    the parameters 'inputs' and 'outputs' need to be set explicitly and that will override 'inputs' parameter
    specified in the Estimator object.

    See example of using this step in notebook https://aka.ms/pl-hyperdrive

    :param name: Name of the step
    :type name: str
    :param hyperdrive_config: A HyperDriveConfig that defines the configuration for this HyperDrive run
    :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
    :param estimator_entry_script_arguments: List of command-line arguments for estimator entry script
    :type estimator_entry_script_arguments: list
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                  azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                  azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param metrics_output: Optional value specifying the location to store HyperDrive run metrics as a JSON file
    :type metrics_output: azureml.pipeline.core.builder.PipelineData, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.graph.OutputPortBinding
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: version
    :type version: str
    """

    _run_config_param_name = 'HyperDriveRunConfig'
    _metrics_output_name = 'MetricsOutputName'

    def __init__(self, name, hyperdrive_config,
                 estimator_entry_script_arguments=None, inputs=None, outputs=None,
                 metrics_output=None, allow_reuse=True, version=None):
        """Initialize a HyperDriveStep.

        :param name: Name of the step
        :type name: str
        :param hyperdrive_config: A HyperDriveConfig that defines the configuration for this HyperDrive run
        :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
        :param estimator_entry_script_arguments: List of command-line arguments for estimator entry script
        :type estimator_entry_script_arguments: list
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                    azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param metrics_output: Optional value specifying the location to store HyperDrive run metrics as a JSON file
        :type metrics_output: azureml.pipeline.core.builder.PipelineData, azureml.data.data_reference.DataReference,
                    azureml.pipeline.core.graph.OutputPortBinding
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: version
        :type version: str
        """
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')

        if estimator_entry_script_arguments is None:
            raise ValueError('estimator_entry_script_arguments is a required parameter. If the Estimator''s entry '
                             'script does not accept commandline arguments, set the parameter value to empty list')

        if hyperdrive_config is None:
            raise ValueError('hyperdrive_config is required')
        from azureml.train.hyperdrive import HyperDriveConfig
        if not isinstance(hyperdrive_config, HyperDriveConfig):
            raise ValueError('Unexpected hyperdrive_config type: {}'.format(type(hyperdrive_config)))

        PipelineStep._process_pipeline_io(estimator_entry_script_arguments, inputs, outputs)

        # resetting estimator args and data refs as we'll use the ones provided to HyperDriveStep
        estimator_run_config = hyperdrive_config._estimator.run_config
        estimator_run_config.arguments = []
        estimator_run_config.data_references = {}

        self._allow_reuse = allow_reuse
        self._version = version

        self._params = {}
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit(
            arguments=estimator_entry_script_arguments)
        self._update_param_bindings()

        self._hyperdrive_config = hyperdrive_config

        if outputs is None:
            outputs = []

        if metrics_output is not None:
            if not isinstance(metrics_output, PipelineData) and not isinstance(metrics_output, DataReference) and \
                    not isinstance(metrics_output, OutputPortBinding):
                raise ValueError("Unexpected metrics_output type: %s" % type(metrics_output))

            if isinstance(metrics_output, DataReference):
                metrics_output = OutputPortBinding(
                    name=metrics_output.data_reference_name,
                    datastore=metrics_output.datastore,
                    bind_mode=metrics_output.mode,
                    path_on_compute=metrics_output.path_on_compute,
                    overwrite=metrics_output.overwrite)

            self._params['MetricsOutputName'] = metrics_output.name

            outputs.append(metrics_output)

        super(HyperDriveStep, self).__init__(name=name, inputs=inputs, outputs=outputs,
                                             arguments=estimator_entry_script_arguments)

    def create_node(self, graph, default_datastore, context):
        """Create a node from this HyperDrive step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        self._params[HyperDriveStep._run_config_param_name] = self._get_hyperdrive_config(context._workspace,
                                                                                          context._experiment_name)

        arguments = self.resolve_input_arguments(self._arguments, self._inputs, self._outputs, self._params)
        if arguments is not None and len(arguments) > 0:
            self._params['Arguments'] = ",".join([str(x) for x in arguments])

        def _get_param_def(param_name):
            is_metadata_param = param_name in (HyperDriveStep._run_config_param_name,
                                               HyperDriveStep._metrics_output_name)

            if param_name in self._pipeline_params_implicit:
                return ParamDef(param_name, is_metadata_param=is_metadata_param, set_env_var=True,
                                env_var_override="AML_PARAMETER_{0}".format(param_name))
            else:
                return ParamDef(param_name, is_metadata_param=is_metadata_param)

        param_defs = [_get_param_def(param_name) for param_name in self._params]

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        module_def = self.create_module_def(execution_type="HyperDriveCloud",
                                            input_bindings=input_bindings,
                                            output_bindings=output_bindings,
                                            param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version)

        module_builder = _InterfaceModuleBuilder(context=context, module_def=module_def)

        node = graph.add_module_node(
            self.name,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_bindings=self._params,
            module_builder=module_builder)

        PipelineStep._configure_pipeline_parameters(graph, node,
                                                    pipeline_params_implicit=self._pipeline_params_implicit)

        return node

    def _get_hyperdrive_config(self, workspace, experiment_name):
        from azureml.train.hyperdrive import _search

        telemetry_values = _search._get_telemetry_values(self._hyperdrive_config, workspace)

        telemetry_values['amlClientType'] = 'azureml-sdk-pipeline'
        telemetry_values['amlClientModule'] = __name__
        telemetry_values['amlClientFunction'] = self.create_node.__name__

        hyperdrive_dto = _search._create_experiment_dto(self._hyperdrive_config, workspace,
                                                        experiment_name, telemetry_values)

        return json.dumps(hyperdrive_dto.as_dict())

    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))


class HyperDriveStepRun(HyperDriveRun):
    """
    HyperDriveStepRun is a HyperDriveRun with additional support from StepRun.

    As a HyperDriveRun this class can be used to manage, check status, and retrieve run details
    for the HyperDrive run and each of the generated child runs.
    For more details on HyperDriveRun and StepRun:
    :class:`azureml.train.hyperdrive.HyperDriveRun`,
    :class:`azureml.pipeline.core.StepRun`

    :param step_run: The step run object which created from pipeline.
    :type step_run: azureml.pipeline.core.StepRun
    """

    def __init__(self, step_run):
        """
        Initialize a hyperdrive step run.

        As a HyperDriveRun this class can be used to manage, check status, and retrieve run details
        for the HyperDrive run and each of the generated child runs.
        For more details on HyperDriveRun and StepRun:
        :class:`azureml.train.hyperdrive.HyperDriveRun`,
        :class:`azureml.pipeline.core.StepRun`

        :param step_run: The step run object which created from pipeline.
        :type step_run: azureml.pipeline.core.StepRun
        """
        step_type = step_run.properties.get('StepType', 'Unknown')
        if step_type != 'HyperDriveStep':
            message = 'Step run with wrong type has been provided. step_type: ' + step_type
            module_logger.error(message)
            raise ValueError(message)

        exp = step_run._experiment
        all_exp_runs = exp.get_runs(include_children=True)

        hyperdrive_run = None
        # TODO: only needed when runid is not linked b/w step and hyperdrive. can be removed after that
        for run in all_exp_runs:
            if run.name == step_run._run_id:
                hyperdrive_run = run

        if not hyperdrive_run:
            child_runs = list(step_run.get_children())
            if len(child_runs) == 1:
                hyperdrive_run = child_runs[0]

        if not hyperdrive_run:
            message = 'Cannot find hyperdrive run from the given step run: ' + step_run.name
            module_logger.error(message)
            raise ValueError(message)

        self._step_run = step_run

        super(self.__class__, self).__init__(exp, hyperdrive_run._run_id)
