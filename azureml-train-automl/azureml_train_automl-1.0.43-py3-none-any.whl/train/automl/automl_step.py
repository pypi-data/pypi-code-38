# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""To add a step to run automated machine learning as part of the Azure Machine Learning pipeline."""
from typing import Any, Dict
import json
import ntpath
from azureml._execution import _commands
from azureml.core import Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core import PipelineStep, PipelineData, TrainingOutput
from azureml.pipeline.core._module_builder import _FolderModuleBuilder
from azureml.pipeline.core.graph import ParamDef
from .automlconfig import AutoMLConfig
from .run import AutoMLRun
from ._azureautomlclient import AzureAutoMLClient
from ._environment_utilities import modify_run_configuration

import os


class AutoMLStep(PipelineStep):
    """Creates a AutoML step in a Pipeline.

    See example of using this step in notebook https://aka.ms/pl-automl

    :param name: Name of the step
    :type name: str
    :param experiment: Experiment to set AutoML config for its run
                       (DEPRECATED) no longer needed
    :type experiment: The azureml.core experiment
    :param automl_config: A AutoMLConfig that defines the configuration for this AutoML run
    :type automl_config: azureml.train.automl.AutoMLConfig
    :param inputs: List of input port bindings
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                  azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData]
    :param outputs: List of output port bindings
    :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
    :param script_repl_params: Optional parameters to be replaced in a script
    :type script_repl_params: dict
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: version
    :type version: str
    :param hash_paths: list of paths to hash to detect a change (script file is always hashed)
    :type hash_paths: list
    """

    DEFAULT_METRIC_PREFIX = 'default_metrics_'
    DEFAULT_MODEL_PREFIX = 'default_model_'

    def __init__(self, name, automl_config, inputs=None, outputs=None, script_repl_params=None,
                 allow_reuse=True, version=None, hash_paths=None, experiment=None):
        """Initialize an AutoMLStep.

        :param name: Name of the step
        :type name: str
        :param experiment: Experiment to set AutoML config for its run
                           (DEPRECATED) no longer needed
        :type experiment: The azureml.core experiment
        :param automl_config: A AutoMLConfig that defines the configuration for this AutoML run
        :type automl_config: azureml.train.automl.AutoMLConfig
        :param inputs: List of input port bindings
        :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                      azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData]
        :param outputs: List of output port bindings
        :type outputs: list[azureml.pipeline.core.builder.PipelineData, azureml.pipeline.core.graph.OutputPortBinding]
        :param script_repl_params: Optional parameters to be replaced in a script
        :type script_repl_params: dict
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: version
        :type version: str
        :param hash_paths: list of paths to hash to detect a change (script file is always hashed)
        :type hash_paths: list
        """
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')

        if experiment:
            print('(DEPRECATED) experiment is no longer needed to create', self.__class__.__name__)

        if automl_config is None:
            raise ValueError('automl_config is required')
        if not isinstance(automl_config, AutoMLConfig):
            raise ValueError('Unexpected automl_config type: {}'.format(type(automl_config)))

        PipelineStep._process_pipeline_io(None, inputs, outputs)

        self._allow_reuse = allow_reuse
        self._version = version

        self._params = {}   # type: Dict[str, Any]
        self._pipeline_params_implicit = PipelineStep._get_pipeline_parameters_implicit()
        self._update_param_bindings()

        self._automl_config = automl_config

        self._source_directory = self._automl_config.user_settings['path']
        self._hash_paths = hash_paths
        if self._hash_paths is None:
            self._hash_paths = []

        ntpath.basename("a/b/c")
        head, tail = ntpath.split(self._automl_config.user_settings["data_script"])
        self._script_name = tail or ntpath.basename(head)

        self._default_metrics_output = None
        self._default_model_output = None

        super(AutoMLStep, self).__init__(name=name, inputs=inputs, outputs=outputs)

        script_path = os.path.join(self._source_directory, self._script_name)
        self._process_script(script_path, script_repl_params)

    def _process_script(self, script_path, script_repl_params):
        import re
        pattern = re.compile(r"@@(?P<param_name>\w+)@@")

        def resolve_input_path(matchobj):
            replacement_str = script_repl_params.get(matchobj.group('param_name'))
            if replacement_str:
                return replacement_str
            else:
                print('found pattern:', matchobj.group('param_name'), ', but no replacement has been provided')

        self._sub_params_in_script(script_path, pattern, resolve_input_path)

    def create_node(self, graph, default_datastore, context):
        """Create a node from this AutoML step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        self._default_metrics_output = PipelineData(name=AutoMLStep.DEFAULT_METRIC_PREFIX + self.name,
                                                    datastore=default_datastore,
                                                    pipeline_output_name='_default_metrics_' + self.name,
                                                    training_output=TrainingOutput(type='Metrics'))
        self._default_model_output = PipelineData(name=AutoMLStep.DEFAULT_MODEL_PREFIX + self.name,
                                                  datastore=default_datastore,
                                                  pipeline_output_name='_default_model_' + self.name,
                                                  training_output=TrainingOutput(type='Model'))

        self._default_metrics_output._set_producer(self)
        self._default_model_output._set_producer(self)
        self._outputs.extend([self._default_metrics_output, self._default_model_output])

        source_directory, hash_paths = self.get_source_directory_and_hash_paths(
            context, self._source_directory, self._script_name, self._hash_paths)

        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        settings = self._get_automl_settings(context)
        self._params.update(settings)

        arguments = self.resolve_input_arguments(self._arguments, self._inputs, self._outputs, self._params)
        if arguments is not None and len(arguments) > 0:
            self._params['Arguments'] = ",".join([str(x) for x in arguments])

        def _get_param_def(param_name):
            if param_name in self._pipeline_params_implicit:
                return ParamDef(param_name, set_env_var=True,
                                env_var_override="AML_PARAMETER_{0}".format(param_name))
            else:
                return ParamDef(param_name, is_optional=True)

        param_defs = [_get_param_def(param_name) for param_name in self._params]

        module_def = self.create_module_def(execution_type="AutoMLCloud",
                                            input_bindings=input_bindings,
                                            output_bindings=output_bindings,
                                            param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version)

        module_builder = _FolderModuleBuilder(
            content_root=source_directory,
            hash_paths=hash_paths,
            context=context,
            module_def=module_def)

        node = graph.add_module_node(
            self.name,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_bindings=self._params,
            module_builder=module_builder)

        PipelineStep._configure_pipeline_parameters(graph, node,
                                                    pipeline_params_implicit=self._pipeline_params_implicit)

        return node

    def _get_automl_settings(self, context):

        self._automl_config._validate_config_settings()
        self._automl_config._get_remove_fit_params()

        user_settings = self._automl_config.user_settings
        automl_client = AzureAutoMLClient(Experiment(context._workspace, context.experiment_name), **user_settings)

        settings = automl_client.automl_settings.as_serializable_dict()

        # parameters for run configuration
        run_configuration = self._automl_config.fit_params['run_configuration']
        if isinstance(run_configuration, str):
            run_config_object = RunConfiguration.load(
                automl_client.automl_settings.path, run_configuration)
        else:
            run_config_object = run_configuration

        try:
            settings['MLCComputeType'] = self._automl_config.fit_params['compute_target'].type
        except KeyError:
            raise KeyError('compute_target is not provided to AutoMLConfig')
        except AttributeError:
            raise AttributeError('compute_target is not an object of ComputeTarget.')

        run_config_object = modify_run_configuration(automl_client.automl_settings,
                                                     run_config_object,
                                                     automl_client.logger)
        run_config_params = self._get_runconfig_as_dict(run_config_object)

        # parameters for CreateParentRunDto
        timeout = None
        if automl_client.automl_settings.iteration_timeout_minutes:
            timeout = automl_client.automl_settings.iteration_timeout_minutes * 60
        settings['max_time_seconds'] = timeout
        settings['target'] = run_config_object.target
        settings['targettype'] = 'mlc'
        settings['num_iterations'] = automl_client.automl_settings.iterations
        settings['training_type'] = None
        settings['acquisition_function'] = None
        settings['metrics'] = 'accuracy'
        settings['primary_metric'] = automl_client.automl_settings.primary_metric
        settings['train_split'] = automl_client.automl_settings.validation_size
        settings['acquisition_parameter'] = 0.0
        settings['num_cross_validation'] = automl_client.automl_settings.n_cross_validations
        settings['data_prep_json_string'] = None
        settings['enable_subsampling'] = automl_client.automl_settings.enable_subsampling

        settings.update(run_config_params)

        for param_name in ('X', 'y', 'sample_weight', 'X_valid',
                           'y_valid', 'sample_weight_valid', 'cv_splits_indices'):
            if param_name in settings and settings[param_name] is not None:
                raise ValueError("""
                                 Passing X, y, sample_weight, X_valid, y_valid, sample_weight_valid or
                                 cv_splits_indices as Pandas or numpy dataframe is only supported for local runs.
                                 For remote runs, please provide X, y, sample_weight, X_valid, y_valid,
                                 sample_weight_valid and cv_splits_indices as azureml.dataprep.Dataflow
                                 objects, or provide a get_data() file instead.
                                 """)

        return settings

    def _get_runconfig_as_dict(self, run_config=None):
        """Set runconfig for AutoML step.

        :param run_config: run config object
        :type run_config: RunConfiguration

        :return: run config params
        :rtype: Dictionary
        """
        if not isinstance(run_config, RunConfiguration):
            raise ValueError('run_configuration is required')

        spark_maven_packages = []
        for package in run_config.environment.spark.packages:
            package_dict = {'artifact': package.artifact, 'group': package.group, 'version': package.version}
            spark_maven_packages.append(package_dict)

        spark_configuration = ';'.join(["{0}={1}".format(key, val) for key, val
                                        in run_config.spark.configuration.items()])

        environment_variables = ';'.join(["{0}={1}".format(key, val) for key, val
                                          in run_config.environment.environment_variables.items()])

        serialized = _commands._serialize_run_config_to_dict(run_config)

        conda_dependencies = None
        try:
            conda_dependencies = serialized['environment']['python']['condaDependencies']
        except KeyError:
            pass

        docker_arguments = None
        if len(run_config.environment.docker.arguments) > 0:
            docker_arguments = ",".join([str(x) for x in run_config.environment.docker.arguments])

        run_config_params = {'Script': run_config.script,
                             'Framework': run_config.framework,
                             'Communicator': run_config.communicator,
                             'AutoPrepareEnvironment': run_config.auto_prepare_environment,
                             'DockerEnabled': run_config.environment.docker.enabled,
                             'BaseDockerImage': run_config.environment.docker.base_image,
                             'SharedVolumes': run_config.environment.docker.shared_volumes,
                             'DockerArguments': docker_arguments,
                             'SparkRepositories': run_config.environment.spark.repositories,
                             'SparkMavenPackages': spark_maven_packages,
                             'SparkConfiguration': spark_configuration,
                             'InterpreterPath': run_config.environment.python.interpreter_path,
                             'UserManagedDependencies': run_config.environment.python.user_managed_dependencies,
                             'GpuSupport': run_config.environment.docker.gpu_support,
                             'MaxRunDurationSeconds': run_config.max_run_duration_seconds,
                             'EnvironmentVariables': environment_variables,
                             'PrecachePackages': run_config.environment.spark.precache_packages,
                             'HistoryOutputCollection': run_config.history.output_collection,
                             'NodeCount': run_config.node_count,
                             'YarnDeployMode': run_config.hdi.yarn_deploy_mode,
                             'CondaDependencies': json.dumps(conda_dependencies),
                             'MpiProcessCountPerNode': run_config.mpi.process_count_per_node,
                             'TensorflowWorkerCount': run_config.tensorflow.worker_count,
                             'TensorflowParameterServerCount': run_config.tensorflow.parameter_server_count,
                             'AMLComputeName': run_config.amlcompute._name,
                             'AMLComputeVmSize': run_config.amlcompute.vm_size,
                             'AMLComputeVmPriority': run_config.amlcompute.vm_priority,
                             'AMLComputeLocation': None,
                             'AMLComputeRetainCluster': run_config.amlcompute._retain_cluster,
                             'AMLComputeNodeCount': run_config.amlcompute._cluster_max_node_count,
                             'SourceDirectoryDataStore': run_config.source_directory_data_store,
                             'DirectoriesToWatch': run_config.history.directories_to_watch
                             }

        return run_config_params

    def _update_param_bindings(self):
        for pipeline_param in self._pipeline_params_implicit.values():
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = pipeline_param
            else:
                raise Exception('Parameter name {0} is already in use'.format(pipeline_param.name))


class AutoMLStepRun(AutoMLRun):
    """
    AutoMLStepRun is AutoMLRun with additional supports from StepRun.

    As AutoMLRun this class can be used to manage, check status, and retrieve run details
    once a AutoML run is submitted. In addition this class can be used to get default outputs
    of AutoMLStep via StepRun.
    For more details on AutoMLRun and StepRun:
    :class:`azureml.train.automl.run.AutoMLRun`,
    :class:`azureml.pipeline.core.StepRun`

    :param step_run: The step run object which created from pipeline.
    :type step_run: azureml.pipeline.core.StepRun
    """

    def __init__(self, step_run):
        """
        Initialize a automl Step run.

        :param step_run: The step run object which created from pipeline.
        :type step_run: azureml.pipeline.core.StepRun
        """
        self._step_run = step_run

        super(self.__class__, self).__init__(step_run._context._experiment, step_run._run_id)

    def get_default_metrics_output(self):
        """
        Return default metrics output of current run.

        :return: Default metrics output of current run.
        :rtype: azureml.pipeline.core.StepRunOutput
        """
        default_metrics_output_name = AutoMLStep.DEFAULT_METRIC_PREFIX + self._step_run._run_name
        return self._step_run.get_output(default_metrics_output_name)

    def get_default_model_output(self):
        """
        Return default model output of current run.

        :return: Default model output of current run.
        :rtype: azureml.pipeline.core.StepRunOutput
        """
        default_model_output_name = AutoMLStep.DEFAULT_MODEL_PREFIX + self._step_run._run_name
        return self._step_run.get_output(default_model_output_name)
