# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""_aeva_provider.py, module for creating/downloading module/datasource,
creating/submitting pipeline runs, fetching for pipeline run status,
retrieving outputs and logs, creating/using published pipelines.
"""
from ._workflow_provider import _PublishedPipelineProvider, _ScheduleProvider, _PipelineEndpointProvider
from ._workflow_provider import _AzureMLModuleProvider, _AzureMLModuleVersionProvider
from ._workflow_provider import _ModuleProvider, _GraphProvider, _DataSourceProvider, _DataTypeProvider
from ._workflow_provider import _PipelineRunProvider, _StepRunProvider, _PortDataReferenceProvider
from .graph import ModuleDef, Module, ParamDef, InputPortDef, OutputPortDef
from .graph import DataSource, DataSourceDef, PublishedPipeline, PortDataReference
from .graph import Graph, ModuleNode, DataSourceNode, DataType, PipelineParameter
from .graph import PipelineDataset
from .schedule import Schedule, ScheduleRecurrence, TimeZone
from .pipeline_endpoint import PipelineEndpoint, PipelineIdVersion
from .module import Module as ModuleElement, ModuleVersion
from .run import StepRunOutput
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._restclient.service_context import ServiceContext
from azureml._restclient.snapshots_client import SnapshotsClient
from azureml.data.data_reference import DataReference
from azureml.core import Datastore
from azureml.data.datapath import DataPath
from azureml.pipeline.core._restclients.aeva.models import PipelineRunCreationInfo, PipelineRunCreationInfoWithGraph
from azureml.pipeline.core._restclients.aeva.models import GraphEntity, GraphModuleNode, GraphEdge, \
    ModuleCreationInfo, EntityInterface, Parameter, DataPathParameter, DataStoreTriggerInfo
from azureml.pipeline.core._restclients.aeva.models import ParameterAssignment, PortInfo, StructuredInterface
from azureml.pipeline.core._restclients.aeva.models import StructuredInterfaceInput, StructuredInterfaceOutput
from azureml.pipeline.core._restclients.aeva.models import StructuredInterfaceParameter, DataSourceCreationInfo
from azureml.pipeline.core._restclients.aeva.models import TrainingOutput
from azureml.pipeline.core._restclients.aeva.models import PipelineCreationInfo, DataTypeCreationInfo
from azureml.pipeline.core._restclients.aeva.models.data_path import DataPath as DataPathModel
from azureml.pipeline.core._restclients.aeva.models import PipelineSubmissionInfo, Recurrence, RecurrenceSchedule
from azureml.pipeline.core._restclients.aeva.models import GraphDatasetNode, OutputSetting, ScheduleCreationInfo, \
    PipelineEndpointCreationInfo, PipelineVersion, DataSetPathParameter
from azureml.pipeline.core._restclients.aeva.models import DataSetDefinition, DataSetDefinitionValue, DataSetReference
from azureml.pipeline.core._restclients.aeva.models import AzureMLModuleCreationInfo
from azureml.pipeline.core._restclients.aeva.models import AzureMLModuleVersionCreationInfo, \
    AzureMLModuleVersionDescriptor
from azureml.pipeline.core._restclients.aeva.service_caller import AE3PServiceCaller


class _AevaModuleSnapshotUploader(object):
    """
    _AevaModuleSnapshotUploader.
    """

    def __init__(self, workspace):
        """Initialize _AevaModuleSnapshotUploader.
        :param workspace: workspace object
        :type workspace: Workspace
        """
        self._workspace = workspace

    def upload(self, directory):
        """Creates a project and snapshot, and return a storage id.
        :param directory: directory
        :type directory: str
        """
        auth = self._workspace._auth_object
        service_context = ServiceContext(  # This can be moved to the constructor
            authentication=auth, subscription_id=self._workspace.subscription_id,
            resource_group_name=self._workspace.resource_group,
            workspace_name=self._workspace.name, workspace_id=self._workspace._workspace_id)

        snapshots_client = SnapshotsClient(service_context)

        storage_id = snapshots_client.create_snapshot(directory)

        return storage_id


class _AevaWorkflowProvider(object):
    """
    _AevaWorkflowProvider.
    """
    def __init__(self, service_caller, module_uploader, workspace=None):
        """Initialize _AevaWorkflowProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param module_uploader: module uploader object
        :type module_uploader: _AevaModuleSnapshotUploader
        :param workspace: workspace object
        :type workspace: Workspace
        """
        self.graph_provider = _AevaGraphProvider(service_caller)
        self.datasource_provider = _AevaDataSourceProvider(service_caller)
        self.module_provider = _AevaModuleProvider(service_caller, module_uploader)
        self.step_run_provider = _AevaStepRunProvider(service_caller)
        self.pipeline_run_provider = _AevaPipelineRunProvider(service_caller, workspace, self.step_run_provider)
        self.published_pipeline_provider = _AevaPublishedPipelineProvider(service_caller, workspace)
        self.port_data_reference_provider = _AevaPortDataReferenceProvider(workspace)
        self.datatype_provider = _AevaDataTypeProvider(service_caller, workspace)
        self.schedule_provider = _AevaScheduleProvider(service_caller, workspace)
        self.pipeline_endpoint_provider = _AevaPipelineEndpointProvider(service_caller, workspace,
                                                                        self.published_pipeline_provider)
        self.azure_ml_module_version_provider = _AevaMlModuleVersionProvider(service_caller,
                                                                             workspace, module_uploader)
        self.azure_ml_module_provider = _AevaMlModuleProvider(service_caller, workspace,
                                                              self.azure_ml_module_version_provider)
        self._service_caller = service_caller

    @staticmethod
    def create_provider(workspace, experiment_name, service_endpoint=None):
        """Creates a workflow provider.
        :param workspace: workspace object
        :type workspace: Workspace
        :param experiment_name: experiment name
        :type experiment_name: str
        :param service_endpoint: service endpoint
        :type service_endpoint: str
        """
        service_caller = _AevaWorkflowProvider.create_service_caller(workspace=workspace,
                                                                     experiment_name=experiment_name,
                                                                     service_endpoint=service_endpoint)
        module_uploader = _AevaModuleSnapshotUploader(workspace)
        return _AevaWorkflowProvider(service_caller, module_uploader, workspace)

    @staticmethod
    def create_service_caller(workspace, experiment_name, service_endpoint=None):
        """Creates a service caller.
        :param workspace: workspace object
        :type workspace: Workspace
        :param experiment_name: experiment name
        :type experiment_name: str
        :param service_endpoint: service endpoint
        :type service_endpoint: str
        """
        if service_endpoint is None:
            service_endpoint = _AevaWorkflowProvider.get_endpoint_url(workspace, experiment_name)

        service_caller = AE3PServiceCaller(
            base_url=service_endpoint,
            workspace=workspace)

        return service_caller

    @staticmethod
    def get_endpoint_url(workspace, experiment_name):
        """Gets an endpoint url.
        :param workspace: workspace object
        :type workspace: Workspace
        :param experiment_name: experiment name
        :type experiment_name: str
        """
        auth = workspace._auth_object
        service_context = ServiceContext(
            authentication=auth, subscription_id=workspace.subscription_id,
            resource_group_name=workspace.resource_group,
            workspace_name=workspace.name, workspace_id=workspace._workspace_id)

        return service_context._get_pipelines_url()


class _AevaModuleProvider(_ModuleProvider):
    """
    _AevaModuleProvider.
    """

    def __init__(self, service_caller, module_uploader):
        """Initialize _AevaModuleProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param module_uploader: module uploader object
        :type module_uploader: _AevaModuleSnapshotUploader
        """
        self._service_caller = service_caller
        self._module_uploader = module_uploader

    @staticmethod
    def module_creation(module_def, content_path, existing_data_types, module_uploader, creation_fn):
        """Creates a module, and returns a module entity id.
        :param module_def: module def
        :type module_def: ModuleDef
        :param content_path: directory
        :type content_path: str
        :param existing_data_types: list of data types
        :type existing_data_types: list[~swagger.models.DataTypeEntity]
        :param module_uploader: module uploader object
        :type module_uploader: _AevaModuleSnapshotUploader
        :param module_uploader: module uploader object
        :type module_uploader: _AevaModuleSnapshotUploader
        :param creation_fn: transforms structured interface, content path to a module entity
        :type creation_fn: function
        :return: ModuleEntity
        :rtype: ~swaggerfixed.models.ModuleEntity
        """
        interface = StructuredInterface(command_line_pattern='', inputs=[], outputs=[], parameters=[],
                                        metadata_parameters=[])
        interface.inputs = []

        existing_data_type_names = set()

        for data_type in existing_data_types:
            existing_data_type_names.add(data_type.id)

        for input in module_def.input_port_defs:
            skip_processing = input.name.startswith(ModuleDef.fake_input_prefix)
            for data_type in input.data_types:
                if data_type not in existing_data_type_names:
                    raise ValueError('DataType %s does not exist, please create it.' % data_type)
            interface.inputs.append(StructuredInterfaceInput(name=input.name, label=input.name,
                                                             data_type_ids_list=input.data_types,
                                                             is_optional=input.is_optional,
                                                             data_store_mode=input.default_datastore_mode,
                                                             path_on_compute=input.default_path_on_compute,
                                                             overwrite=input.default_overwrite,
                                                             data_reference_name=input.default_data_reference_name,
                                                             skip_processing=skip_processing,
                                                             is_resource=input.is_resource))

        interface.outputs = []
        for output in module_def.output_port_defs:
            skip_processing = output.name.startswith(ModuleDef.fake_output_name)
            if output.data_type not in existing_data_type_names:
                raise ValueError('DataType %s does not exist, please create it.' % output.data_type)
            if not output.training_output:
                training_output = None
            else:
                training_output = TrainingOutput(training_output_type=output.training_output.type,
                                                 iteration=output.training_output.iteration,
                                                 metric=output.training_output.metric)
            interface.outputs.append(StructuredInterfaceOutput(name=output.name, label=output.name,
                                                               data_type_id=output.data_type,
                                                               data_store_name=output.default_datastore_name,
                                                               data_store_mode=output.default_datastore_mode,
                                                               path_on_compute=output.default_path_on_compute,
                                                               overwrite=output.default_overwrite,
                                                               data_reference_name=output.name,
                                                               training_output=training_output,
                                                               skip_processing=skip_processing))

        for param in module_def.param_defs:
            if isinstance(param.default_value, PipelineParameter):
                default = param.default_value.default_value
            else:
                default = param.default_value
            structured_param = StructuredInterfaceParameter(name=param.name, parameter_type='String',
                                                            is_optional=param.is_optional,
                                                            default_value=default,
                                                            set_environment_variable=param.set_env_var,
                                                            environment_variable_override=param.env_var_override)
            if param.is_metadata_param:
                interface.metadata_parameters.append(structured_param)
            else:
                interface.parameters.append(structured_param)

        storage_id = None
        is_interface_only = True
        if content_path is not None:
            is_interface_only = False
            storage_id = module_uploader.upload(directory=content_path)

        return creation_fn(interface, storage_id, is_interface_only)

    def create_module(self, module_def, content_path=None, fingerprint=None):
        """Creates a module, and returns a module entity id.
        :param module_def: module def
        :type module_def: ModuleDef
        :param content_path: directory
        :type content_path: str
        :param fingerprint: fingerprint
        :type fingerprint: str
        :return: the module id
        :rtype: str
        """

        def creation_fn(structured_interface, storage_id, is_interface_only):
            properties = global_tracking_info_registry.gather_all(content_path or '.')
            creation_info = ModuleCreationInfo(name=module_def.name, description=module_def.description,
                                               is_deterministic=module_def.allow_reuse,
                                               module_execution_type=module_def.module_execution_type,
                                               structured_interface=structured_interface,
                                               identifier_hash=fingerprint,
                                               storage_id=storage_id, is_interface_only=is_interface_only,
                                               properties=properties)
            return self._service_caller.create_module_async(creation_info=creation_info)

        module_entity = _AevaModuleProvider.module_creation(module_def, content_path,
                                                            self._service_caller.get_all_datatypes_async(),
                                                            self._module_uploader, creation_fn)
        return module_entity.id

    def download(self, module_id):
        """Downloads a module.
        :param module_id: module id
        :type module_id: str
        """
        module_info = self._service_caller.get_module_async(id=module_id)
        return _AevaModuleProvider.from_module_info(module_info)

    def find_module_by_fingerprint(self, fingerprint):
        """Search module by fingerprint.
        :param fingerprint: fingerprint
        :type fingerprint: str
        """
        module_info = self._service_caller.try_get_module_by_hash_async(fingerprint)
        # only reuse a module if its upload state is Completed ('1')
        if module_info is None or not (module_info.data.upload_state == '1' or
                                       module_info.data.upload_state == 'Completed'):
            return None

        return _AevaModuleProvider.from_module_info(module_info)

    @staticmethod
    def from_module_info(module_info):
        """Returns a module object with a given module info.
        :param module_info: module info
        :type module_info: ModuleInfo
        """
        entity_interface = module_info.interface
        module_entity = module_info.data

        # Populate a ModuleDef based on the entity/interface
        param_defs = []
        for parameter in entity_interface.parameters:
            param_defs.append(
                ParamDef(name=parameter.name, default_value=parameter.default_value, is_metadata_param=False))
        for parameter in entity_interface.metadata_parameters:
            param_defs.append(
                ParamDef(name=parameter.name, default_value=parameter.default_value, is_metadata_param=True))

        structured_inputs = {}
        for structured_input in module_entity.structured_interface.inputs:
            structured_inputs[structured_input.name] = structured_input
        input_port_defs = []
        for input_port in entity_interface.ports.inputs:
            structured_input = structured_inputs[input_port.name]
            input_port_defs.append(
                InputPortDef(name=input_port.name, data_types=input_port.data_types_ids,
                             default_path_on_compute=structured_input.path_on_compute,
                             default_datastore_mode=structured_input.data_store_mode,
                             default_overwrite=structured_input.overwrite,
                             default_data_reference_name=structured_input.data_reference_name)
            )

        structured_outputs = {}
        for structured_output in module_entity.structured_interface.outputs:
            structured_outputs[structured_output.name] = structured_output
        output_port_defs = []
        for output_port in entity_interface.ports.outputs:
            structured_output = structured_outputs[output_port.name]
            output_port_defs.append(
                OutputPortDef(name=output_port.name, default_datastore_name=structured_output.data_store_name,
                              default_datastore_mode=structured_output.data_store_mode,
                              default_path_on_compute=structured_output.path_on_compute,
                              is_directory=(structured_output.data_type_id == "AnyDirectory"),
                              data_type=structured_output.data_type_id, default_overwrite=structured_output.overwrite,
                              training_output=structured_output.training_output)
            )

        module_def = ModuleDef(name=module_entity.name,
                               description=module_entity.description,
                               input_port_defs=input_port_defs,
                               output_port_defs=output_port_defs,
                               param_defs=param_defs,
                               allow_reuse=module_entity.is_deterministic)

        return Module(module_id=module_entity.id, module_def=module_def)


class _AevaDataSourceProvider(_DataSourceProvider):
    """
    _AevaDataSourceProvider.
    """

    def __init__(self, service_caller):
        """Initialize _AevaDataSourceProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        """
        self._service_caller = service_caller

    def upload(self, datasource_def, fingerprint=None):
        """Upload a datasource, and returns a datasource entity id.
        :param datasource_def:datasource def
        :type datasource_def: DatasourceDef
        :param fingerprint: fingerprint
        :type fingerprint: str
        """
        sp_params = datasource_def.sql_stored_procedure_params
        if sp_params is not None:
            from azureml.pipeline.core._restclients.aeva.models import StoredProcedureParameter
            sp_params = [StoredProcedureParameter(name=p.name, value=p.value, type=p.type.value) for p in sp_params]

        creation_info = DataSourceCreationInfo(name=datasource_def.name,
                                               data_type_id=datasource_def.data_type_id,
                                               description=datasource_def.description,
                                               data_store_name=datasource_def.datastore_name,
                                               path_on_data_store=datasource_def.path_on_datastore,
                                               sql_table_name=datasource_def.sql_table,
                                               sql_query=datasource_def.sql_query,
                                               sql_stored_procedure_name=datasource_def.sql_stored_procedure,
                                               sql_stored_procedure_params=sp_params,
                                               identifier_hash=fingerprint)

        datasource_entity = self._service_caller.create_datasource_async(creation_info=creation_info)
        return datasource_entity.id

    def download(self, datasource_id):
        """Download a datasource, and returns a _AevaDataSourceProvider.
        :param datasource_id:datasource id
        :type datasource_id: str
        """
        datasource_entity = self._service_caller.get_datasource_async(id=datasource_id)
        return _AevaDataSourceProvider.from_datasource_entity(datasource_entity)

    def find_datasource_by_fingerprint(self, fingerprint):
        """Search datasource with a given fingerprint, returns a _AevaDataSourceProvider.
        :param fingerprint: fingerprint
        :type fingerprint: str
        """
        datasource_entity = self._service_caller.try_get_datasource_by_hash_async(fingerprint)
        if datasource_entity is None:
            return None

        return _AevaDataSourceProvider.from_datasource_entity(datasource_entity)

    @staticmethod
    def from_datasource_entity(datasource_entity):
        """Returns a Datasource with a given datasource entity.
        :param datasource_entity: datasource entity
        :type datasource_entity: DataSourceEntity
        """
        datasource_def = DataSourceDef(datasource_entity.name,
                                       description=datasource_entity.description,
                                       data_type_id=datasource_entity.data_type_id)

        if datasource_entity.data_location is not None and datasource_entity.data_location.data_reference is not None:
            # TODO: The backend is switching from int values for enums to string values
            # After this is complete, we can remove the code that checks for int values
            type = datasource_entity.data_location.data_reference.type
            if type == '1' or type == 'AzureBlob':
                data_reference = datasource_entity.data_location.data_reference.azure_blob_reference
                datasource_def.path_on_datastore = data_reference.relative_path
            elif type == '2' or type == 'AzureDataLake':
                data_reference = datasource_entity.data_location.data_reference.azure_data_lake_reference
                datasource_def.path_on_datastore = data_reference.relative_path
            elif type == '3' or type == 'AzureFiles':
                data_reference = datasource_entity.data_location.data_reference.azure_files_reference
                datasource_def.path_on_datastore = data_reference.relative_path
            elif type == '4' or type == 'AzureSqlDatabase':
                data_reference = datasource_entity.data_location.data_reference.azure_sql_database_reference
                _AevaDataSourceProvider.update_datasource_def(data_reference, datasource_def)
            elif type == '5' or type == 'AzurePostgresDatabase':
                data_reference = datasource_entity.data_location.data_reference.azure_postgres_database_reference
                _AevaDataSourceProvider.update_datasource_def(data_reference, datasource_def)
            elif type == '6' or type == 'AzureDataLakeGen2Reference':
                data_reference = datasource_entity.data_location.data_reference.azure_data_lake_gen2_reference
                datasource_def.path_on_datastore = data_reference.relative_path
            else:
                raise ValueError("Unsupported datasource data reference type")
            datasource_def.datastore_name = data_reference.aml_data_store_name

        return DataSource(datasource_entity.id, datasource_def)

    @staticmethod
    def update_datasource_def(data_reference, datasource_def):
        """Update datasource from a database reference
        :param data_reference: database reference
        :type data_reference: AzureDatabaseReference
        :param datasource_def: definition of a datasource.
        :type datasource_def: DataSourceDef
        """
        datasource_def.sql_table = data_reference.table_name
        datasource_def.sql_query = data_reference.sql_query
        datasource_def.sql_stored_procedure = data_reference.stored_procedure_name
        sp_params = data_reference.stored_procedure_parameters
        if sp_params is not None:
            from azureml.pipeline.core.graph import StoredProcedureParameter, StoredProcedureParameterType
            sp_params = [StoredProcedureParameter(name=p.name, value=p.value,
                                                  type=StoredProcedureParameterType.from_str(p.type))
                         for p in sp_params]
        datasource_def.sql_stored_procedure_params = sp_params


class _AevaGraphProvider(_GraphProvider):
    """
    _AevaGraphProvider.
    """

    def __init__(self, service_caller):
        """Initialize _AevaGraphProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        """
        self._service_caller = service_caller

    def submit(self, graph, pipeline_parameters, continue_on_step_failure, experiment_name, parent_run_id=None):
        """Submit a pipeline run.
        :param graph: graph
        :type graph: Graph
        :param pipeline_parameters: Parameters to pipeline execution
        :type pipeline_parameters: dict
        :param continue_on_step_failure: continue on step failure
        :type continue_on_step_failure: bool
        :param experiment_name: experiment name
        :type experiment_name: str
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        """
        created_pipeline_run_id = self.create_pipeline_run(graph=graph, pipeline_parameters=pipeline_parameters,
                                                           continue_on_step_failure=continue_on_step_failure,
                                                           experiment_name=experiment_name)
        self._service_caller.submit_saved_pipeline_run_async(pipeline_run_id=created_pipeline_run_id,
                                                             parent_run_id=parent_run_id)
        print('Submitted pipeline run:', created_pipeline_run_id)

        return created_pipeline_run_id

    def create_pipeline_run(self, graph, pipeline_parameters, continue_on_step_failure, experiment_name):
        """Create an unsubmitted pipeline run.
        :param graph: graph
        :type graph: Graph
        :param pipeline_parameters: Parameters to pipeline execution
        :type pipeline_parameters: dict
        :param continue_on_step_failure: continue on step failure
        :type continue_on_step_failure: bool
        :param experiment_name: experiment name
        :type experiment_name: str
        """
        aeva_graph = _AevaGraphProvider._build_graph(graph)
        if pipeline_parameters is not None:
            for param_name in pipeline_parameters:
                if param_name not in graph.params:
                    raise Exception('Assertion failure. Validation of pipeline_params should have failed')

        graph_parameter_assignment, graph_datapath_assignment = \
            _AevaGraphProvider._get_parameter_assignments(pipeline_parameters)
        dataset_definition_assignment = _AevaGraphProvider._get_data_set_definition_assignments(graph)

        pipeline_run_submission = PipelineRunCreationInfoWithGraph()
        pipeline_run_submission.creation_info = \
            PipelineRunCreationInfo(description=graph._name,
                                    parameter_assignments=graph_parameter_assignment,
                                    data_path_assignments=graph_datapath_assignment,
                                    data_set_definition_value_assignments=dataset_definition_assignment,
                                    continue_experiment_on_node_failure=continue_on_step_failure,
                                    run_source='SDK',
                                    run_type='SDK')
        pipeline_run_submission.graph = aeva_graph
        graph_interface = _AevaGraphProvider._get_graph_interface(graph)
        pipeline_run_submission.graph_interface = graph_interface
        _AevaGraphProvider._validate_parameter_types(pipeline_parameters, graph_interface)

        created_pipeline_run = self._service_caller.create_unsubmitted_pipeline_run_async(
            pipeline_run_submission, experiment_name=experiment_name)

        return created_pipeline_run.id

    @staticmethod
    def _validate_parameter_types(pipeline_parameters, graph_interface):
        if pipeline_parameters is not None:
            for graph_interface_param in graph_interface.parameters:
                if graph_interface_param.name in pipeline_parameters:
                    param_type = _AevaGraphProvider.\
                        _get_backend_param_type_code(pipeline_parameters[graph_interface_param.name])
                    if not isinstance(pipeline_parameters[graph_interface_param.name], DataPath):
                        if param_type != graph_interface_param.type:
                            graph_interface_param_type_name = \
                                _AevaGraphProvider._get_sdk_param_type_name(graph_interface_param.type)
                            param_value = pipeline_parameters[graph_interface_param.name]
                            param_value_type = type(param_value).__name__
                            raise Exception('Expected type of the pipeline parameter {0} is {1}, but the value '
                                            '{2} provided is of type {3}'.format(graph_interface_param.name,
                                                                                 graph_interface_param_type_name,
                                                                                 str(param_value),
                                                                                 param_value_type))

    def create_graph_from_run(self, context, pipeline_run_id):
        """Creates the graph from the pipeline_run_id.
        :param context: context object
        :type context: _GraphContext
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        """
        pipeline_run = self._service_caller.get_pipeline_run_async(pipeline_run_id)
        graph_entity = self._service_caller.get_graph_async(pipeline_run.graph_id)

        graph = Graph(name=pipeline_run.description, context=context)

        # add modules
        for module_node in graph_entity.module_nodes:
            node_id = module_node.id

            module_info = self._service_caller.get_module_async(module_node.module_id)

            module = _AevaModuleProvider.from_module_info(module_info)

            node = ModuleNode(graph=graph, name=module_info.data.name, node_id=node_id, module=module)

            # set param value overrides
            for parameter in module_node.module_parameters:
                node.get_param(parameter.name).set_value(parameter.value)
            for parameter in module_node.module_metadata_parameters:
                node.get_param(parameter.name).set_value(parameter.value)

            graph._add_node_to_dicts(node)

        for datasource_node in graph_entity.dataset_nodes:
            node_id = datasource_node.id
            datasource_entity = self._service_caller.get_datasource_async(datasource_node.dataset_id)
            datasource = _AevaDataSourceProvider.from_datasource_entity(datasource_entity)
            node = DataSourceNode(graph=graph, name=datasource_entity.name, node_id=node_id, datasource=datasource)
            graph._add_node_to_dicts(node)

        # add edges
        for edge in graph_entity.edges:
            if edge.destination_input_port.graph_port_name is not None:
                output = graph._nodes[edge.source_output_port.node_id].get_output(
                    edge.source_output_port.port_name)
                output.pipeline_output_name = edge.destination_input_port.graph_port_name
                graph._pipeline_outputs[output.pipeline_output_name] = output
            else:
                input_port = graph._nodes[edge.destination_input_port.node_id].get_input(
                    edge.destination_input_port.port_name)
                input_port.connect(graph._nodes[edge.source_output_port.node_id].get_output(
                    edge.source_output_port.port_name))

        return graph

    @staticmethod
    def _get_data_set_definition_assignments(graph):
        dataset_assignments = {}
        for param_name, param_value in graph.params.items():
            dv = param_value.default_value
            if isinstance(dv, PipelineDataset) or PipelineDataset.is_dataset(dv):
                if isinstance(dv, PipelineDataset):
                    dv = dv.dataset
                try:
                    id = dv.id
                    version = dv.definition_version
                except AttributeError:
                    id = dv._dataset_id
                    version = dv._version_id
                ref = DataSetReference(id=id, version=version)
                dataset_assignments[param_name] = DataSetDefinitionValue(data_set_reference=ref)

        return dataset_assignments

    @staticmethod
    def _get_parameter_assignments(pipeline_params):
        param_assignment = {}
        datapath_assignment = {}
        if pipeline_params is not None:
            for param_name, param_value in pipeline_params.items():
                # type of the param is preserved in EntityInterface
                if not isinstance(pipeline_params[param_name], DataPath):
                    pipeline_param_value_type = type(pipeline_params[param_name])
                    if pipeline_param_value_type not in [str, int, float, bool]:
                        raise Exception('Invalid parameter type {0}'.format(str(pipeline_param_value_type)))
                    param_assignment[param_name] = str(pipeline_params[param_name])
                else:
                    datapath = pipeline_params[param_name]
                    datapath_model = DataPathModel(data_store_name=datapath.datastore_name,
                                                   relative_path=datapath.path_on_datastore)
                    datapath_assignment[param_name] = datapath_model

        return param_assignment, datapath_assignment

    @staticmethod
    def _build_graph(graph):
        """
        Generate the graph entity to submit to the aeva backend.
        :return the graph entity
        :rtype GraphEntity
        """
        graph_entity = GraphEntity()
        graph_entity.sub_graph_nodes = []
        graph_entity.dataset_nodes = []
        graph_entity.module_nodes = []
        graph_entity.edges = []

        for node_id in graph._nodes:
            node = graph._nodes[node_id]

            if node._module is not None:
                module_node = GraphModuleNode(id=node_id, module_id=node._module.id)
                module_node.module_parameters = []
                module_node.module_metadata_parameters = []

                module_node.module_output_settings = []
                for output in node.outputs:
                    skip_processing = output.name.startswith(ModuleDef.fake_output_name)
                    if not skip_processing:
                        output_setting = OutputSetting(name=output.name, data_store_name=output.datastore_name,
                                                       data_store_mode=output.bind_mode,
                                                       path_on_compute=output.path_on_compute,
                                                       overwrite=output.overwrite,
                                                       data_reference_name=output.name)
                        module_node.module_output_settings.append(output_setting)

                    # add edge for graph output
                    if output.pipeline_output_name is not None:
                        source = PortInfo(node_id=node.node_id, port_name=output.name)
                        dest = PortInfo(graph_port_name=output.pipeline_output_name)
                        graph_entity.edges.append(GraphEdge(source_output_port=source, destination_input_port=dest))

                # TODO:  Support node-level settings for inputs

                for param_name in node._params:
                    param = node.get_param(param_name)
                    value = param.value
                    # TODO: Use an enum for value_type
                    if isinstance(value, PipelineParameter):
                        # value is of type PipelineParameter, use its name property
                        # TODO parameter assignment expects 'Literal', 'GraphParameterName', 'Concatenate', 'Input'??
                        param_assignment = ParameterAssignment(name=param.name, value=value.name, value_type=1)
                    else:
                        param_assignment = ParameterAssignment(name=param.name, value=value, value_type=0)

                    if param.param_def.is_metadata_param:
                        module_node.module_metadata_parameters.append(param_assignment)
                    else:
                        module_node.module_parameters.append(param_assignment)

                graph_entity.module_nodes.append(module_node)

            elif node._datasource is not None:
                if not node.datapath_param_name:
                    if node._datasource.id:
                        dataset_node = GraphDatasetNode(id=node_id, dataset_id=node._datasource.id)
                    else:
                        pipeline_dataset = node._datasource.datasource_def._pipeline_dataset
                        if pipeline_dataset.parameter_name:
                            dataset_def = DataSetDefinition(
                                data_type_short_name=pipeline_dataset._data_type_short_name,
                                parameter_name=pipeline_dataset.parameter_name
                            )
                        else:
                            dataset_def_val = _AevaGraphProvider._dataset_def_val_from_dataset(pipeline_dataset)
                            dataset_def = DataSetDefinition(
                                data_type_short_name=pipeline_dataset._data_type_short_name,
                                value=dataset_def_val
                            )
                        dataset_node = GraphDatasetNode(id=node_id, data_set_definition=dataset_def)
                else:
                    dataset_node = GraphDatasetNode(id=node_id, dataset_id=None,
                                                    data_path_parameter_name=node.datapath_param_name)
                graph_entity.dataset_nodes.append(dataset_node)

        for edge in graph.edges:
            source = PortInfo(node_id=edge.source_port.node.node_id, port_name=edge.source_port.name)
            dest = PortInfo(node_id=edge.dest_port.node.node_id, port_name=edge.dest_port.name)
            graph_entity.edges.append(GraphEdge(source_output_port=source, destination_input_port=dest))

        return graph_entity

    @staticmethod
    def _dataset_def_val_from_dataset(pipeline_dataset):
        dataset_ref = DataSetReference(id=pipeline_dataset.dataset_id,
                                       version=pipeline_dataset.dataset_version)
        return DataSetDefinitionValue(data_set_reference=dataset_ref)

    @staticmethod
    def _get_backend_param_type_code(param_value):
        # ParameterType enum in the backend is Int=0, Double=1, Bool=2, String=3, Unidentified=4
        param_type_code = 4
        if isinstance(param_value, int):
            param_type_code = 0
        elif isinstance(param_value, float):
            param_type_code = 1
        elif isinstance(param_value, bool):
            param_type_code = 2
        elif isinstance(param_value, str):
            param_type_code = 3

        return param_type_code

    @staticmethod
    def _get_sdk_param_type_name(backend_param_type_code):
        # ParameterType enum in the backend is Int=0, Double=1, Bool=2, String=3, Unidentified=4
        param_type_code = 'Unidentified'
        if backend_param_type_code == 0:
            return int.__name__
        elif backend_param_type_code == 1:
            return float.__name__
        elif backend_param_type_code == 2:
            return bool.__name__
        elif backend_param_type_code == 3:
            return str.__name__

        return param_type_code

    @staticmethod
    def _get_graph_interface(graph):
        parameters = []
        datapath_parameters = []
        new_datapaths_params = []
        for param_name, pipeline_param_value in graph.params.items():  # param is of type PipelineParameter
            if isinstance(pipeline_param_value.default_value, DataPath):
                # param_type_code = _AevaGraphProvider._get_backend_param_type_code(pipeline_param_value.default_value)
                datapath_defaultval = pipeline_param_value.default_value
                datapath_model = DataPathModel(data_store_name=datapath_defaultval.datastore_name,
                                               relative_path=datapath_defaultval.path_on_datastore)
                # TODO Get the datatype from the graph
                datapath_parameter = DataPathParameter(name=param_name, default_value=datapath_model,
                                                       is_optional=True, data_type_id='AnyFile')
                datapath_parameters.append(datapath_parameter)
            elif isinstance(pipeline_param_value.default_value, PipelineDataset):
                dataset_def_val = _AevaGraphProvider._dataset_def_val_from_dataset(pipeline_param_value.default_value)
                dataset_path_param = DataSetPathParameter(param_name, default_value=dataset_def_val,
                                                          is_optional=True, documentation='DataPath')
                new_datapaths_params.append(dataset_path_param)
            else:
                param_type_code = _AevaGraphProvider._get_backend_param_type_code(pipeline_param_value.default_value)
                parameters.append(Parameter(name=param_name, default_value=pipeline_param_value.default_value,
                                            is_optional=True, type=param_type_code))

        return EntityInterface(parameters=parameters, data_path_parameters=datapath_parameters,
                               data_path_parameter_list=new_datapaths_params)


class _AevaPipelineRunProvider(_PipelineRunProvider):
    """
    _AevaPipelineRunProvider.
    """

    def __init__(self, service_caller, workspace, step_run_provider):
        """Initialize _AevaPipelineRunProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param workspace: workspace object
        :type workspace: Workspace
        :param step_run_provider: step run provider object
        :type step_run_provider: _AevaStepRunProvider
        """
        self._service_caller = service_caller
        self._step_run_provider = step_run_provider
        self._workspace = workspace

    def get_status(self, pipeline_run_id):
        """
        Get the current status of the run
        :return current status
        :rtype str
        """
        result = self._service_caller.get_pipeline_run_async(pipeline_run_id)

        if result.status is None:
            status_code = 'NotStarted'
        else:
            status_code = result.status.status_code

        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if status_code == '0':
            return "NotStarted"
        elif status_code == '1':
            return "Running"
        elif status_code == '2':
            return "Failed"
        elif status_code == '3':
            return "Finished"
        elif status_code == '4':
            return "Canceled"
        else:
            return status_code

    def cancel(self, pipeline_run_id):
        """Cancel the run.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        """
        self._service_caller.cancel_pipeline_run_async(pipeline_run_id)

    def get_node_statuses(self, pipeline_run_id):
        """Gets the status of the node.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        """
        return self._service_caller.get_all_nodes_in_level_status_async(pipeline_run_id)

    def get_pipeline_output(self, context, pipeline_run_id, pipeline_output_name):
        """Get the pipeline output.
        :param context: context
        :type context: _GraphContext
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param pipeline_output_name: pipeline output name
        :type pipeline_output_name: str
        """
        output = self._service_caller.get_pipeline_run_output_async(pipeline_run_id, pipeline_output_name)
        data_reference = _AevaPortDataReferenceProvider.get_data_reference_from_output(self._workspace,
                                                                                       output,
                                                                                       pipeline_output_name)

        return PortDataReference(context=context, pipeline_run_id=pipeline_run_id, data_reference=data_reference)

    def get_pipeline_experiment_name(self, pipeline_run_id):
        """Gets experiment name.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        """
        return self._service_caller.get_pipeline_run_async(pipeline_run_id).run_history_experiment_name

    def get_runs_by_pipeline_id(self, pipeline_id):
        """Gets pipeline runs for a published pipeline ID.
        :param pipeline_id: published pipeline id
        :type pipeline_id: str
        :return List of tuples of (run id, experiment name)
        :rtype List
        """
        pipeline_run_entities = self._service_caller.get_pipeline_runs_by_pipeline_id_async(pipeline_id)
        return [(pipeline_run.id, pipeline_run.run_history_experiment_name) for pipeline_run in pipeline_run_entities]


class _AevaStepRunProvider(_StepRunProvider):
    """
    _AevaStepRunProvider.
    """

    def __init__(self, service_caller):
        """Initialize _AevaStepRunProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        """
        self._service_caller = service_caller

    def get_status(self, pipeline_run_id, node_id):
        """
        Get the current status of the node run
        :return current status
        :rtype str
        """
        result = self._service_caller.get_node_status_code_async(pipeline_run_id, node_id)

        if result is None:
            status_code = '0'
        else:
            status_code = result

        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if status_code == '0':
            return "NotStarted"
        elif status_code == '1':
            return "Queued"
        elif status_code == '2':
            return "Running"
        elif status_code == '3':
            return "Failed"
        elif status_code == '4':
            return "Finished"
        elif status_code == '5':
            return "Canceled"
        elif status_code == '6':
            return "PartiallyExecuted"
        elif status_code == '7':
            return "Bypassed"
        else:
            return status_code

    def get_run_id(self, pipeline_run_id, node_id):
        """Gets run id.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param node_id: node id
        :type node_id: str
        """
        return self._service_caller.get_node_status_async(pipeline_run_id, node_id).run_id

    def get_job_log(self, pipeline_run_id, node_id):
        """Gets job log.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param node_id: node id
        :type node_id: str
        """
        return self._service_caller.get_node_job_log_async(pipeline_run_id, node_id)

    def get_stdout_log(self, pipeline_run_id, node_id):
        """Gets stdout log.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param node_id: node id
        :type node_id: str
        """
        return self._service_caller.get_node_stdout_log_async(pipeline_run_id, node_id)

    def get_stderr_log(self, pipeline_run_id, node_id):
        """Gets stderr log.
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param node_id: node id
        :type node_id: str
        """
        return self._service_caller.get_node_stderr_log_async(pipeline_run_id, node_id)

    def get_outputs(self, step_run, context, pipeline_run_id, node_id):
        """Gets outputs of pipeline run.
        :param step_run: step run object
        :type step_run: StepRun
        :param context: context object
        :type context: _GraphContext
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param node_id: node id
        :type node_id: str
        """
        node_outputs = self._service_caller.get_node_outputs_async(pipeline_run_id, node_id)

        output_port_runs = {}
        # remove fake completion output
        for node_output_name in node_outputs.keys():
            if node_output_name != ModuleDef.fake_output_name:
                output_port_runs[node_output_name] = StepRunOutput(context, pipeline_run_id, step_run,
                                                                   node_output_name, node_outputs[node_output_name])

        return output_port_runs

    def get_output(self, step_run, context, pipeline_run_id, node_id, name):
        """Gets an output of pipeline run.
        :param step_run: step run object
        :type step_run: StepRun
        :param context: context object
        :type context: _GraphContext
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param node_id: node id
        :type node_id: str
        :param name: name
        :type name: str
        """
        node_outputs = self._service_caller.get_node_outputs_async(pipeline_run_id, node_id)
        return StepRunOutput(context, pipeline_run_id, step_run, name, node_outputs[name])


class _AevaPublishedPipelineProvider(_PublishedPipelineProvider):
    """
    _AevaPublishedPipelineProvider.
    """

    def __init__(self, service_caller, workspace):
        """Initialize _AevaPublishedPipelineProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param workspace: workspace object
        :type workspace: Workspace
        """
        self._service_caller = service_caller
        self._workspace = workspace

    def create_from_pipeline_run(self, name, description, version, pipeline_run_id, continue_run_on_step_failure=None):
        """Create a published pipeline from a run.
        :param name: name
        :type name: str
        :param description: description
        :type description: str
        :param version: version
        :type version: str
        :param pipeline_run_id: pipeline run id
        :type pipeline_run_id: str
        :param continue_run_on_step_failure: Whether to continue execution of other steps if a step fails, optional.
        :type continue_run_on_step_failure: bool
        """
        pipeline_run = self._service_caller.get_pipeline_run_async(pipeline_run_id)
        graph_entity = self._service_caller.get_graph_async(pipeline_run.graph_id)
        graph_interface = self._service_caller.get_graph_interface_async(pipeline_run.graph_id)

        properties = global_tracking_info_registry.gather_all()

        creation_info = PipelineCreationInfo(name=name,
                                             description=description,
                                             version=version,
                                             graph=graph_entity,
                                             graph_interface=graph_interface,
                                             continue_run_on_step_failure=continue_run_on_step_failure,
                                             properties=properties)

        pipeline_entity = self._service_caller.create_pipeline_async(pipeline_creation_info=creation_info)
        return _AevaPublishedPipelineProvider.from_pipeline_entity(self._workspace, pipeline_entity, self)

    def create_from_graph(self, name, description, version, graph, continue_run_on_step_failure=None):
        """Create a published pipeline from an in-memory graph
        :param name: name
        :type name: str
        :param description: description
        :type description: str
        :param version: version
        :type version: str
        :param graph: graph
        :type graph: Graph
        :param continue_run_on_step_failure: Whether to continue execution of other steps if a step fails, optional.
        :type continue_run_on_step_failure: bool
        """
        graph_entity = _AevaGraphProvider._build_graph(graph)
        graph_interface = _AevaGraphProvider._get_graph_interface(graph)
        dataset_definition_assignment = _AevaGraphProvider._get_data_set_definition_assignments(graph)

        properties = global_tracking_info_registry.gather_all()

        creation_info = PipelineCreationInfo(name=name,
                                             description=description,
                                             version=version,
                                             graph=graph_entity,
                                             graph_interface=graph_interface,
                                             data_set_definition_value_assignments=dataset_definition_assignment,
                                             continue_run_on_step_failure=continue_run_on_step_failure,
                                             properties=properties)

        pipeline_entity = self._service_caller.create_pipeline_async(pipeline_creation_info=creation_info)
        return _AevaPublishedPipelineProvider.from_pipeline_entity(self._workspace, pipeline_entity, self)

    def get_published_pipeline(self, published_pipeline_id):
        """Gets a published pipeline with a given published pipeline id.
        :param published_pipeline_id: published pipeline id
        :type published_pipeline_id: str
        """
        pipeline_entity = self._service_caller.get_pipeline_async(pipeline_id=published_pipeline_id)
        return _AevaPublishedPipelineProvider.from_pipeline_entity(self._workspace, pipeline_entity, self)

    def submit(self, published_pipeline_id, experiment_name, parameter_assignment=None, parent_run_id=None,
               continue_run_on_step_failure=None):
        """Submits a pipeline_run with a given published pipeline id.
        :param published_pipeline_id: published pipeline id
        :type published_pipeline_id: str
        :param experiment_name: The experiment name
        :type experiment_name: str
        :param parameter_assignment: parameter assignment
        :type parameter_assignment: {str: str}
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        :param continue_run_on_step_failure: Whether to continue execution of other steps if a step fails, optional.
                                             If provided, overrides the continue on step failure setting of the
                                             Pipeline.
        :type continue_run_on_step_failure: bool
        """
        graph_parameter_assignment, graph_datapath_assignment = \
            _AevaGraphProvider._get_parameter_assignments(parameter_assignment)

        properties = global_tracking_info_registry.gather_all()

        pipeline_submission_info = PipelineSubmissionInfo(experiment_name=experiment_name,
                                                          description=experiment_name,
                                                          run_source='SDK',
                                                          run_type='SDK',
                                                          parameter_assignments=graph_parameter_assignment,
                                                          data_path_assignments=graph_datapath_assignment,
                                                          continue_run_on_step_failure=continue_run_on_step_failure,
                                                          properties=properties)
        created_pipeline_run = self._service_caller.submit_pipeline_run_from_pipeline_async(
            pipeline_id=published_pipeline_id, pipeline_submission_info=pipeline_submission_info,
            parent_run_id=parent_run_id)
        return created_pipeline_run.id

    def get_all(self, active_only=True):
        """
        Get all published pipelines in the current workspace

        :param active_only: If true, only return published pipelines which are currently active.
        :type active_only Bool

        :return: a list of :class:`azureml.pipeline.core.graph.PublishedPipeline`
        :rtype: list
        """
        entities = self._service_caller.get_all_published_pipelines(active_only=active_only)
        return [_AevaPublishedPipelineProvider.from_pipeline_entity(
            self._workspace, entity, self) for entity in entities]

    @staticmethod
    def from_pipeline_entity(workspace, pipeline_entity, _pipeline_provider=None):
        """Returns a PublishedPipeline.
        :param workspace: workspace object
        :type workspace: Workspace
        :param pipeline_entity: pipeline entity
        :type pipeline_entity: PipelineEntity
        :param _pipeline_provider: The published pipeline provider.
        :type _pipeline_provider: _PublishedPipelineProvider
        """
        status = AE3PServiceCaller.entity_status_from_enum(pipeline_entity.entity_status)
        return PublishedPipeline(workspace=workspace,
                                 name=pipeline_entity.name,
                                 description=pipeline_entity.description,
                                 graph_id=pipeline_entity.graph_id,
                                 version=pipeline_entity.version,
                                 published_pipeline_id=pipeline_entity.id,
                                 status=status,
                                 endpoint=pipeline_entity.url,
                                 total_run_steps=pipeline_entity.total_run_steps,
                                 continue_on_step_failure=pipeline_entity.continue_run_on_step_failure,
                                 _pipeline_provider=_pipeline_provider)

    def set_status(self, pipeline_id, new_status):
        """Set the status of the published pipeline ('Active', 'Deprecated', or 'Disabled').
        :param pipeline_id: published pipeline id
        :type pipeline_id: str
        :param new_status: The status to set
        :type new_status: str
        """
        self._service_caller.update_published_pipeline_status_async(pipeline_id=pipeline_id, new_status=new_status)


class _AevaPortDataReferenceProvider(_PortDataReferenceProvider):
    """
    _AevaPortDataReferenceProvider.
    """

    def __init__(self, workspace):
        """Initializes _AevaPortDataReferenceProvider.
        :param workspace: workspace
        :type workspace: Workspace
        """
        self._workspace = workspace

    def create_port_data_reference(self, output_run):
        """Creates a port data reference.
        :param output_run: output run
        :type output_run: output run
        """
        step_output = output_run.step_output
        data_reference = self.get_data_reference_from_output(self._workspace, step_output, output_run.name)

        return PortDataReference(context=output_run.context, pipeline_run_id=output_run.pipeline_run_id,
                                 data_reference=data_reference, step_run=output_run.step_run)

    @staticmethod
    def get_data_reference_from_output(workspace, output, name):
        """Convert from a NodeOutput to a data references.
        :param workspace: the workspace
        :type workspace: Workspace
        :param output: output
        :type output: NodeOutput
        :param name: name for the data reference
        :type name: str
        """
        if output.data_location is not None and output.data_location.data_reference is not None:
            type = output.data_location.data_reference.type
            # TODO: The backend is switching from int values for enums to string values
            # After this is complete, we can remove the code that checks for int values
            if type == '1' or type == 'AzureBlob':
                data_location = output.data_location.data_reference.azure_blob_reference
            elif type == '2' or type == 'AzureDataLake':
                data_location = output.data_location.data_reference.azure_data_lake_reference
            elif type == '3' or type == 'AzureFiles':
                data_location = output.data_location.data_reference.azure_files_reference
            elif type == '4' or type == 'AzureSqlDatabase':
                data_location = output.data_location.data_reference.azure_sql_database_reference
            elif type == '5' or type == 'AzurePostgresDatabase':
                data_location = output.data_location.data_reference.azure_postgres_database_reference
            elif type == '6' or type == 'AzureDataLakeGen2Reference':
                data_location = output.data_location.data_reference.azure_data_lake_gen2_reference
            else:
                raise ValueError("Unsupported output data reference type: " + type)
            datastore = Datastore(workspace, data_location.aml_data_store_name)
            return DataReference(datastore=datastore,
                                 data_reference_name=name,
                                 path_on_datastore=data_location.relative_path)
        else:
            return None

    def download(self, datastore_name, path_on_datastore, local_path, overwrite, show_progress):
        """download from datastore.
        :param datastore_name: datastore name
        :type datastore_name: str
        :param path_on_datastore: path on datastore
        :type path_on_datastore: str
        :param local_path: local path
        :type local_path: str
        :param overwrite: overwrite existing file
        :type overwrite: bool
        :param show_progress: show progress of download
        :type show_progress: bool
        """
        datastore = Datastore(self._workspace, datastore_name)

        return datastore.download(target_path=local_path, prefix=path_on_datastore, overwrite=overwrite,
                                  show_progress=show_progress)


class _AevaDataTypeProvider(_DataTypeProvider):
    """
    _AevaDataTypeProvider.
    """
    def __init__(self, service_caller, workspace):
        """Initialize _AevaDataTypeProvider.
        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param workspace: workspace object
        :type workspace: Workspace
        """
        self._service_caller = service_caller
        self._workspace = workspace

    def get_all_datatypes(self):
        """Get all data types."""
        entities = self._service_caller.get_all_datatypes_async()
        datatypes = [_AevaDataTypeProvider.from_datatype_entity(self._workspace, entity) for entity in entities]
        return datatypes

    def create_datatype(self, id, name, description, is_directory=False, parent_datatype_ids=None):
        """Create a datatype.
        :param id: id
        :type id: str
        :param name: name
        :type name: str
        :param description: description
        :type description: str
        :param is_directory: is directory
        :type is_directory: bool
        :param parent_datatype_ids: parent datatype ids
        :type parent_datatype_ids: list[str]
        """
        if parent_datatype_ids is None:
            parent_datatype_ids = []
        creation_info = DataTypeCreationInfo(id=id, name=name, description=description,
                                             is_directory=is_directory,
                                             parent_data_type_ids=parent_datatype_ids)
        entity = self._service_caller.create_datatype_async(creation_info)
        return _AevaDataTypeProvider.from_datatype_entity(self._workspace, entity)

    def update_datatype(self, id, new_description=None, new_parent_datatype_ids=None):
        """Create a datatype.
        :param id: id
        :type id: str
        :param new_description: new description
        :type new_description: str
        :param new_parent_datatype_ids: parent datatype ids to add
        :type new_parent_datatype_ids: list[str]
        """
        datatypes = self._service_caller.get_all_datatypes_async()

        if id == 'AnyFile' or id == 'AnyDirectory' or id == 'AzureBlobReference' or id == 'AzureDataLakeReference'\
                or id == 'AzureFilesReference':
            raise ValueError('Cannot update a required DataType.')

        datatype_entity = None

        for datatype in datatypes:
            if datatype.id == id:
                datatype_entity = datatype

        if datatype_entity is None:
            raise ValueError('Cannot update DataType with name %s as it does not exist.' % id)

        if new_description is not None:
            datatype_entity.description = new_description

        if new_parent_datatype_ids is not None:
            if datatype_entity.parent_data_type_ids is None:
                datatype_entity.parent_data_type_ids = new_parent_datatype_ids
            else:
                datatype_entity.parent_data_type_ids = list(set().union(datatype_entity.parent_data_type_ids,
                                                                        new_parent_datatype_ids))

        entity = self._service_caller.update_datatype_async(id, datatype_entity)
        return _AevaDataTypeProvider.from_datatype_entity(self._workspace, entity)

    def ensure_default_datatypes(self):
        """Checks if the datatype exists or not.  Creates one if not."""
        ids = [datatype.id for datatype in self.get_all_datatypes()]

        required_file_types = ['AnyFile', 'AzureBlobReference', 'AzureDataLakeReference', 'AzureFilesReference',
                               'AzureSqlDatabaseReference', 'AzurePostgresDatabaseReference',
                               'AzureDataLakeGen2Reference']

        required_directory_types = ['AnyDirectory']

        for file_type in required_file_types:
            if file_type not in ids:
                self.create_datatype(id=file_type, name=file_type, description=file_type, is_directory=False)
        for dir_type in required_directory_types:
            if dir_type not in ids:
                self.create_datatype(id=dir_type, name=dir_type, description=dir_type, is_directory=True)

    @staticmethod
    def from_datatype_entity(workspace, datatype_entity):
        """Create a datatype.
        :param workspace: workspace object
        :type workspace: Workspace
        :param datatype_entity: datatype entity
        :type datatype_entity: DataTypeEntity
        """
        return DataType(workspace=workspace, id=datatype_entity.id, name=datatype_entity.name,
                        description=datatype_entity.description, is_directory=datatype_entity.is_directory,
                        parent_datatype_ids=datatype_entity.parent_data_type_ids)


class _AevaScheduleProvider(_ScheduleProvider):
    """
    _AevaScheduleProvider.
    """
    def __init__(self, service_caller, workspace):
        """Initialize _AevaScheduleProvider.

        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param workspace: workspace object
        :type workspace: Workspace
        """
        self._service_caller = service_caller
        self._workspace = workspace

    def create_schedule(self, name, published_pipeline_id, experiment_name, recurrence=None,
                        datastore_name=None, polling_interval=None, data_path_parameter_name=None,
                        description=None, pipeline_parameters=None, continue_on_step_failure=None,
                        path_on_datastore=None):
        """Creates a schedule.

        :param name: The name of the schedule.
        :type name: str
        :param published_pipeline_id: The id of the pipeline to submit.
        :type published_pipeline_id: str
        :param experiment_name: The experiment name to submit runs with.
        :type experiment_name: str
        :param recurrence: The name of the schedule.
        :type recurrence: azureml.pipeline.core.ScheduleRecurrence
        :param datastore_name: The name of the datastore to monitor for modified/added blobs.
        :type datastore_name: str
        :param polling_interval: How long, in minutes, between polling for modified/added blobs.
        :type polling_interval: int
        :param data_path_parameter_name: The name of the data path pipeline parameter to set
                                         with the changed blob path.
        :type data_path_parameter_name: str
        :param description: The description of the schedule.
        :type description: str
        :param pipeline_parameters: The dict of pipeline parameters.
        :type pipeline_parameters: dict
        :param continue_on_step_failure: Whether to continue execution of other steps in the submitted PipelineRun
                                         if a step fails. If provided, this will override the continue_on_step_failure
                                         setting for the Pipeline.
        :type continue_on_step_failure: bool
        :param path_on_datastore: The path on the datastore to monitor for modified/added blobs.
        :type path_on_datastore: str
        """
        recurrence_entity = None
        data_store_trigger_info = None
        if recurrence is not None:
            schedule_type = '0'
            if recurrence.hours is None and recurrence.minutes is None and recurrence.week_days is None:
                recurrence_schedule = None
            else:
                recurrence_schedule = RecurrenceSchedule(hours=recurrence.hours, minutes=recurrence.minutes,
                                                         week_days=recurrence.week_days)

            recurrence_entity = Recurrence(frequency=recurrence.frequency, interval=recurrence.interval,
                                           start_time=recurrence.start_time, time_zone=recurrence.time_zone,
                                           schedule=recurrence_schedule)
        else:
            schedule_type = '1'
            data_store_trigger_info = DataStoreTriggerInfo(data_store_name=datastore_name,
                                                           polling_interval=polling_interval,
                                                           data_path_parameter_name=data_path_parameter_name,
                                                           path_on_data_store=path_on_datastore)

        graph_parameter_assignment, graph_datapath_assignment = \
            _AevaGraphProvider._get_parameter_assignments(pipeline_parameters)

        properties = global_tracking_info_registry.gather_all()

        pipeline_submission_info = PipelineSubmissionInfo(experiment_name=experiment_name, description=description,
                                                          parameter_assignments=graph_parameter_assignment,
                                                          data_path_assignments=graph_datapath_assignment,
                                                          continue_run_on_step_failure=continue_on_step_failure,
                                                          properties=properties)
        schedule_creation_info = ScheduleCreationInfo(name=name, pipeline_id=published_pipeline_id,
                                                      pipeline_submission_info=pipeline_submission_info,
                                                      recurrence=recurrence_entity, schedule_type=schedule_type,
                                                      data_store_trigger_info=data_store_trigger_info)

        schedule_entity = self._service_caller.create_schedule_async(schedule_creation_info)
        if schedule_entity.provisioning_status == '2':
            raise SystemError("Provisioning of schedule", schedule_entity.id,
                              "failed. Please try again or contact support.")
        return self.from_schedule_entity(schedule_entity, self._workspace, self)

    def get_schedule(self, schedule_id):
        """Gets a schedule with a given id.

        :param schedule_id: The schedule id
        :type schedule_id: str
        """
        schedule_entity = self._service_caller.get_schedule_async(schedule_id=schedule_id)
        return self.from_schedule_entity(schedule_entity, self._workspace, self)

    def get_schedule_provisioning_status(self, schedule_id):
        """Gets the provisioning status of a schedule with a given id.

        :param schedule_id: The schedule id
        :type schedule_id: str
        """
        schedule_entity = self._service_caller.get_schedule_async(schedule_id=schedule_id)
        return AE3PServiceCaller.provisioning_status_from_enum(schedule_entity.provisioning_status)

    def get_schedules_by_pipeline_id(self, pipeline_id):
        """
        Get all schedules for given pipeline id.

        :param pipeline_id: The pipeline id.
        :type pipeline_id str

        :return: a list of :class:`azureml.pipeline.core.Schedule`
        :rtype: list
        """
        entities = self._service_caller.get_schedules_by_pipeline_id_async(pipeline_id=pipeline_id)
        return [self.from_schedule_entity(entity, self._workspace, self) for entity in entities]

    def update_schedule(self, schedule_id, name=None, description=None, recurrence=None, pipeline_parameters=None,
                        status=None, datastore_name=None, polling_interval=None, data_path_parameter_name=None,
                        continue_on_step_failure=None, path_on_datastore=None):
        """Updates a schedule.

        :param schedule_id: The id of the schedule to update.
        :type schedule_id: str
        :param name: The name of the schedule.
        :type name: str
        :param recurrence: The name of the schedule.
        :type recurrence: azureml.pipeline.core.ScheduleRecurrence
        :param description: The description of the schedule.
        :type description: str
        :param pipeline_parameters: The dict of pipeline parameters.
        :type pipeline_parameters: dict
        :param status: The new status.
        :type status: str
        :param datastore_name: The name of the datastore to monitor for modified/added blobs.
        :type datastore_name: str
        :param polling_interval: How long, in minutes, between polling for modified/added blobs.
        :type polling_interval: int
        :param data_path_parameter_name: The name of the data path pipeline parameter to set
                                         with the changed blob path.
        :type data_path_parameter_name: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the submitted PipelineRun
                                         if a step fails. If provided, this will override the continue_on_step_failure
                                         setting for the Pipeline.
        :type continue_on_step_failure: bool
        :param path_on_datastore: The path on the datastore to monitor for modified/added blobs.
        :type path_on_datastore: str
        """
        updated = self._service_caller.get_schedule_async(schedule_id)

        schedule_type = updated.schedule_type

        if recurrence is None:
            recurrence = updated.recurrence
        else:
            if recurrence.hours is None and recurrence.minutes is None and recurrence.week_days is None:
                recurrence_schedule = None
            else:
                recurrence_schedule = RecurrenceSchedule(hours=recurrence.hours, minutes=recurrence.minutes,
                                                         week_days=recurrence.week_days)
            recurrence = Recurrence(frequency=recurrence.frequency, interval=recurrence.interval,
                                    start_time=recurrence.start_time, time_zone=recurrence.time_zone,
                                    schedule=recurrence_schedule)

        data_store_trigger_info = None
        if schedule_type == '1' or schedule_type == 'DataStore':
            data_store_trigger_info = updated.data_store_trigger_info
            if datastore_name is None:
                datastore_name = data_store_trigger_info.data_store_name
            if polling_interval is None:
                polling_interval = data_store_trigger_info.polling_interval
            if data_path_parameter_name is None:
                data_path_parameter_name = data_store_trigger_info.data_path_parameter_name
            if path_on_datastore is None:
                path_on_datastore = data_store_trigger_info.path_on_data_store
            data_store_trigger_info.data_store_name = datastore_name
            data_store_trigger_info.polling_interval = polling_interval
            data_store_trigger_info.data_path_parameter_name = data_path_parameter_name
            data_store_trigger_info.path_on_data_store = path_on_datastore

        if description is None:
            description = updated.pipeline_submission_info.description
        if name is None:
            name = updated.name
        if status is None:
            status = updated.entity_status
        if continue_on_step_failure is None:
            continue_on_step_failure = updated.pipeline_submission_info.continue_run_on_step_failure

        graph_parameter_assignment, graph_datapath_assignment = \
            _AevaGraphProvider._get_parameter_assignments(pipeline_parameters)
        if pipeline_parameters is None:
            graph_parameter_assignment = updated.pipeline_submission_info.parameter_assignments
            graph_datapath_assignment = updated.pipeline_submission_info.data_path_assignments

        properties = global_tracking_info_registry.gather_all()

        submission_info = PipelineSubmissionInfo(experiment_name=updated.pipeline_submission_info.experiment_name,
                                                 description=description,
                                                 parameter_assignments=graph_parameter_assignment,
                                                 data_path_assignments=graph_datapath_assignment,
                                                 run_type=updated.pipeline_submission_info.run_type,
                                                 schedule_id=updated.pipeline_submission_info.schedule_id,
                                                 continue_run_on_step_failure=continue_on_step_failure,
                                                 properties=properties)

        updated.name = name
        updated.entity_status = status
        updated.recurrence = recurrence
        updated.pipeline_submission_info = submission_info
        updated.data_store_trigger_info = data_store_trigger_info

        schedule_entity = self._service_caller.update_schedule_async(schedule_id, updated)
        if schedule_entity.provisioning_status == '2' or schedule_entity.provisioning_status == 'Failed':
            raise SystemError("Provisioning of schedule", schedule_entity.id,
                              "failed. Please try again or contact support.")
        return self.from_schedule_entity(schedule_entity, self._workspace, self)

    def get_all_schedules(self, active_only=True):
        """
        Get all schedules in the current workspace

        :param active_only: If true, only return schedules which are currently active.
        :type active_only Bool

        :return: a list of :class:`azureml.pipeline.core.Schedule`
        :rtype: list
        """
        entities = self._service_caller.get_all_schedules_async(active_only=active_only)
        return [self.from_schedule_entity(entity, self._workspace, self) for entity in entities]

    def set_status(self, schedule_id, new_status):
        """Set the status of the schedule ('Active', 'Deprecated', or 'Disabled').

        :param schedule_id: published pipeline id
        :type schedule_id: str
        :param new_status: The status to set
        :type new_status: str
        """
        self.update_schedule(schedule_id=schedule_id, status=new_status)

    def get_pipeline_runs_for_schedule(self, schedule_id):
        """Gets pipeline runs for a schedule ID.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return List of tuples of (run id, experiment name)
        :rtype List
        """
        pipeline_run_entities = self._service_caller.get_pipeline_runs_by_schedule_id_async(schedule_id)
        return [(pipeline_run.id, pipeline_run.run_history_experiment_name) for pipeline_run in
                pipeline_run_entities]

    def get_last_pipeline_run_for_schedule(self, schedule_id):
        """Gets the latest pipeline run for a schedule ID.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return Tuple of (run id, experiment name)
        :rtype Tuple
        """
        pipeline_run = self._service_caller.get_last_pipeline_run_by_schedule_id_async(schedule_id)
        if pipeline_run is None:
            return None, None
        return pipeline_run.id, pipeline_run.run_history_experiment_name

    @staticmethod
    def from_schedule_entity(schedule_entity, workspace, schedule_provider):
        """Returns a Schedule.

        :param schedule_entity: schedule entity
        :type schedule_entity: PipelineScheduleEntity
        :param workspace: workspace object
        :type workspace: Workspace
        :param schedule_provider: The schedule provider.
        :type schedule_provider: _ScheduleProvider
        """
        status = AE3PServiceCaller.entity_status_from_enum(schedule_entity.entity_status)

        datastore_name = None
        polling_interval = None
        data_path_parameter_name = None
        path_on_datastore = None
        recurrence = None
        if schedule_entity.schedule_type == '0' or schedule_entity.schedule_type == 'Recurrence':
            frequency = AE3PServiceCaller.frequency_from_enum(schedule_entity.recurrence.frequency)
            hours = None
            minutes = None
            week_days = None
            recurrence_schedule = schedule_entity.recurrence.schedule
            if recurrence_schedule is not None:
                hours = recurrence_schedule.hours
                minutes = recurrence_schedule.minutes
                week_days = AE3PServiceCaller.week_days_from_enum(recurrence_schedule.week_days)

            if schedule_entity.recurrence.time_zone is None:
                time_zone = None
            else:
                time_zone = TimeZone(schedule_entity.recurrence.time_zone)

            recurrence = ScheduleRecurrence(frequency=frequency,
                                            interval=schedule_entity.recurrence.interval,
                                            start_time=schedule_entity.recurrence.start_time,
                                            time_zone=time_zone,
                                            hours=hours,
                                            minutes=minutes,
                                            week_days=week_days)
        else:
            datastore_name = schedule_entity.data_store_trigger_info.data_store_name
            polling_interval = schedule_entity.data_store_trigger_info.polling_interval
            data_path_parameter_name = schedule_entity.data_store_trigger_info.data_path_parameter_name
            path_on_datastore = schedule_entity.data_store_trigger_info.path_on_data_store

        description = None
        continue_on_step_failure = None
        submission_info = schedule_entity.pipeline_submission_info
        if submission_info is not None:
            description = submission_info.description
            continue_on_step_failure = submission_info.continue_run_on_step_failure

        return Schedule(id=schedule_entity.id,
                        name=schedule_entity.name,
                        description=description,
                        pipeline_id=schedule_entity.pipeline_id,
                        status=status,
                        recurrence=recurrence,
                        workspace=workspace,
                        datastore_name=datastore_name,
                        polling_interval=polling_interval,
                        data_path_parameter_name=data_path_parameter_name,
                        continue_on_step_failure=continue_on_step_failure,
                        path_on_datastore=path_on_datastore,
                        _schedule_provider=schedule_provider)


class _AevaPipelineEndpointProvider(_PipelineEndpointProvider):
    """
    _AevaPipelineEndpointProvider.
    """
    def __init__(self, service_caller, workspace, published_pipeline_provider):
        """Initialize _AevaPipelineEndpointProvider.

        :param service_caller: service caller object
        :type service_caller: ServiceCaller
        :param workspace: workspace object
        :type workspace: Workspace
        :param published_pipeline_provider: _AevaPublishedPipelineProvider object
        :type published_pipeline_provider: _AevaPublishedPipelineProvider
        """
        self._service_caller = service_caller
        self._workspace = workspace
        self._published_pipeline_provider = published_pipeline_provider

    def create_pipeline_endpoint(self, name, description, pipeline_id):
        """Creates a PipelineEndpoint.

        :param name: The name of the PipelineEndpoint.
        :type name: str
        :param description: The description of the PipelineEndpoint.
        :type name: str
        :param pipeline_id: The id of the pipeline maps to defaultVersion.
        :type pipeline_id: str
        """
        properties = global_tracking_info_registry.gather_all()

        pipeline_endpoint_creation_info = PipelineEndpointCreationInfo(name=name, description=description,
                                                                       pipeline_id=pipeline_id, properties=properties)

        pipeline_endpoint_entity = self._service_caller.create_pipeline_endpoint_async(pipeline_endpoint_creation_info)

        return self.from_pipeline_endpoint_entity(pipeline_endpoint_entity, self._workspace, self,
                                                  self._published_pipeline_provider)

    def get_pipeline_endpoint(self, endpoint_id=None, name=None):
        """Get PipelineEndpoint either by Id or Name.

        :param endpoint_id: Id of PipelineEndpoint
        :type endpoint_id: str
        :param name: Name of PipelineEndpoint
        :type name: str
        :return: an object of :class:`azureml.pipeline.core.PipelineEndpoint`
        :rtype:
         :class:`azureml.pipeline.core.PipelineEndpoint`
        """
        if endpoint_id is not None:
            pipeline_endpoint_entity = self._service_caller.get_pipeline_endpoint_by_id_async(endpoint_id)
            return self.from_pipeline_endpoint_entity(pipeline_endpoint_entity, self._workspace,
                                                      self, self._published_pipeline_provider)

        if name is not None:
            pipeline_endpoint_entity = self._service_caller.get_pipeline_endpoint_by_name_async(name)
            return self.from_pipeline_endpoint_entity(pipeline_endpoint_entity, self._workspace, self,
                                                      self._published_pipeline_provider)
        raise Exception('Please, enter either id or name to get PipelineEndpoint')

    def update_pipeline_endpoint(self, endpoint_id, version=None, name=None, pipeline_id=None, description=None,
                                 status=None, add_default=False):
        """Update PipelineEndpoint

        :param endpoint_id: The PipelineEndpoint id
        :type endpoint_id: str
        :param version: The version to set as default version
        :type version: str
        :param name: The name to set for PipelineEndpoint
        :type name: str
        :param pipeline_id: The pipeline id to add
        :type pipeline_id: str
        :param description: The description of PipelineEndpoint
        :type description: str
        :param status: The new status of PipelineEndpoint.
        :type status: str
        :param add_default: The flag to set default version after adding pipeline
        :type add_default: bool
        :return: an object of :class:`azureml.pipeline.core.PipelineEndpoint`
        :rtype:
         :class:`azureml.pipeline.core.PipelineEndpoint`
        """
        updated_pe = self._service_caller.get_pipeline_endpoint_by_id_async(endpoint_id)
        if name is not None:
            updated_pe.name = name
        if version is not None:
            updated_pe.default_version = version
        if description is not None:
            updated_pe.description = description
        if status is not None:
            updated_pe.entity_status = status
        if pipeline_id is not None:
            if any(version.pipeline_id == pipeline_id for version in updated_pe.pipeline_version_list):
                raise ValueError("Cannot add pipeline , pipeline id %s exists in PipelineEndpoint {%s}"
                                 % (pipeline_id, updated_pe.id))
            version = str(int(max(item.version for item in updated_pe.pipeline_version_list)) + 1)
            updated_pe.pipeline_version_list.append(PipelineVersion(
                pipeline_id=pipeline_id, version=version))
            if add_default is True:
                updated_pe.default_version = version
        pipeline_endpoint_entity = self._service_caller.update_pipeline_endpoint_async(endpoint_id, updated_pe)
        return self.from_pipeline_endpoint_entity(pipeline_endpoint_entity, self._workspace, self,
                                                  self._published_pipeline_provider)

    def get_all_pipeline_endpoints(self, active_only=True):
        """Get all PipelineEndpoints.

        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: a list of :class:`azureml.pipeline.core.PipelineEndpoint`
        :rtype: list
        """
        pipeline_endpoint_entity = self._service_caller.get_all_pipeline_endpoints_async(active_only)

        return \
            [self.from_pipeline_endpoint_entity(entity, self._workspace, self, self._published_pipeline_provider)
             for entity in pipeline_endpoint_entity]

    def submit_pipeline_run_from_pipeline_endpoint(self, endpoint_id, experiment_name, parameter_assignment=None,
                                                   parent_run_id=None, pipeline_version=None):
        """SubmitPipelineRunFromPipelineEndpointAsync.

        :param endpoint_id: The PipelineEndpoint id
        :type endpoint_id: str
        :param experiment_name: The experiment name
        :type experiment_name: str
        :param parameter_assignment: parameter assignment
        :type parameter_assignment: {str: str}
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        :param pipeline_version: The version of pipeline to submit,
         optional
        :type pipeline_version: str
        """
        graph_parameter_assignment, graph_datapath_assignment = \
            _AevaGraphProvider._get_parameter_assignments(parameter_assignment)

        properties = global_tracking_info_registry.gather_all()

        pipeline_submission_info = PipelineSubmissionInfo(experiment_name=experiment_name,
                                                          description=experiment_name,
                                                          run_source='SDK',
                                                          run_type='SDK',
                                                          parameter_assignments=graph_parameter_assignment,
                                                          data_path_assignments=graph_datapath_assignment,
                                                          properties=properties)
        created_pipeline_run_id = self._service_caller.submit_pipeline_run_from_pipeline_endpoint_async(
            endpoint_id=endpoint_id, pipeline_submission_info=pipeline_submission_info,
            parent_run_id=parent_run_id, pipeline_version=pipeline_version)
        return created_pipeline_run_id.id

    def get_all_pipelines_from_pipeline_endpoint(self, endpoint_id, active_only=True):
        """get_all_pipelines_from_pipeline_endpoint_async.

        :param endpoint_id: The pipeline endpoint id
        :type endpoint_id: str
        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.PipelineEntity]
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        pipeline_entity_list = self._service_caller.get_all_pipelines_from_pipeline_endpoint_async(endpoint_id,
                                                                                                   active_only)

        return \
            [self._published_pipeline_provider.from_pipeline_entity(self._workspace, entity,
                                                                    self._published_pipeline_provider)
             for entity in pipeline_entity_list]

    @staticmethod
    def from_pipeline_endpoint_entity(pipeline_endpoint_entity, workspace, pipeline_endpoint_provider,
                                      published_pipeline_provider):
        """Returns a PipelineEndpoint.

        :param pipeline_endpoint_entity: PipelineEndpoint entity
        :type pipeline_endpoint_entity: PipelineEndpointEntity
        :param workspace: workspace object
        :type workspace: Workspace
        :param pipeline_endpoint_provider: The PipelineEndpoint provider.
        :type pipeline_endpoint_provider: _PipelineEndpointProvider
        :param published_pipeline_provider: The PublishedPipeline provider.
        :type published_pipeline_provider: _AevaPublishedPipelineProvider
        """

        version_list = [PipelineIdVersion(version=pipeline_version.version, pipeline_id=pipeline_version.pipeline_id)
                        for pipeline_version in pipeline_endpoint_entity.pipeline_version_list]

        status = AE3PServiceCaller.entity_status_from_enum(pipeline_endpoint_entity.entity_status)

        result = PipelineEndpoint(workspace=workspace, id=pipeline_endpoint_entity.id,
                                  name=pipeline_endpoint_entity.name,
                                  description=pipeline_endpoint_entity.description,
                                  status=status,
                                  default_version=pipeline_endpoint_entity.default_version,
                                  endpoint=pipeline_endpoint_entity.url,
                                  pipeline_version_list=version_list,
                                  _pipeline_endpoint_provider=pipeline_endpoint_provider,
                                  _published_pipeline_provider=published_pipeline_provider)
        return result


class _AevaMlModuleProvider(_AzureMLModuleProvider):
        """
        _AevaMlModuleProvider.
        """
        def __init__(self, service_caller, workspace, module_version_provider):
            """Initialize _AzureMLModuleProvider.

            :param service_caller: service caller object
            :type service_caller: ServiceCaller
            :param workspace: workspace object
            :type workspace: Workspace
            :param module_version_provider: _AevaMLModuleVersionProvider object
            :type module_version_provider: _AevaMLModuleVersionProvider
            """
            self._service_caller = service_caller
            self._workspace = workspace
            self._module_version_provider = module_version_provider

        @staticmethod
        def from_azure_ml_module_entity(azure_ml_module_entity, workspace, azure_ml_module_provider,
                                        azure_ml_module_version_provider):

            """ Returns a Module.

                :param azure_ml_module_entity: AzureMLModule entity
                    :type azure_ml_module_entity: AzureMLModule
                    :param workspace: workspace object
                    :type workspace: Workspace
                    :param azure_ml_module_provider: The Module provider.
                    :type azure_ml_module_provider: _AevaMlModuleProvider
                    :param azure_ml_module_version_provider: The ModuleVersion provider.
                    :type azure_ml_module_version_provider: _AevaMlModuleVersionProvider
                    """
            version_list = []
            if azure_ml_module_entity.versions is not None:
                version_list = [AzureMLModuleVersionDescriptor(version=module_version.version,
                                                               module_version_id=module_version.module_version_id)
                                for module_version in azure_ml_module_entity.versions]
            status = AE3PServiceCaller.entity_status_from_enum(azure_ml_module_entity.entity_status)
            result = ModuleElement(workspace=workspace, module_id=azure_ml_module_entity.id,
                                   name=azure_ml_module_entity.name,
                                   description=azure_ml_module_entity.description,
                                   status=status,
                                   default_version=azure_ml_module_entity.default_version,
                                   module_version_list=version_list,
                                   _module_provider=azure_ml_module_provider,
                                   _module_version_provider=azure_ml_module_version_provider)
            return result

        def create_module(self, name, description):
            """Creates an AzureML module.

            :param name: The name of the AzureML module.
            :type name: str
            :param description: The description of the AzureML module.
            :type name: str
            """
            creation_info = AzureMLModuleCreationInfo(name=name, description=description)
            entity = self._service_caller.create_azure_ml_module_async(creation_info)
            return self.from_azure_ml_module_entity(entity, self._workspace, self,
                                                    self._module_version_provider)

        def get_module(self, module_id=None, name=None):
            """Get Module either by Id or Name.

            :param module_id: Id of Module
            :type module_id: str
            :param name: Name of Module
            :type name: str
            :return: an object of :class:`azureml.pipeline.core.Module`
            :rtype:
             :class:`azureml.pipeline.core.Module`
            """
            if module_id is not None:
                entity = self._service_caller.get_azure_ml_module_by_id_async(module_id)
                return self.from_azure_ml_module_entity(entity, self._workspace, self,
                                                        self._module_version_provider)

            if name is not None:
                entity = self._service_caller.get_azure_ml_module_by_name_async(name)
                return self.from_azure_ml_module_entity(entity, self._workspace, self,
                                                        self._module_version_provider)
            raise Exception('Neither id nor name was provided to get Module')

        def update_module(self, module_id, name=None, description=None,
                          status=None, default_version=None, versions=None):
            """Update Module

            :param module_id: The Module id
            :type module_id: str
            :param name: The name to set for Module
            :type name: str
            :param description: The description of Module
            :type description: str
            :param status: The new status of Module.
            :type status: str
            :param default_version: The default version of the Module
            :type default_version: str
            :param versions: A list of the contained ModuleVersions
            :type versions: a list of :class:`azureml.pipeline.core.ModuleVersion`
            :return: an object of :class:`azureml.pipeline.core.Module`
            :rtype:
             :class:`azureml.pipeline.core.Module`
            """
            updated = self._service_caller.get_azure_ml_module_by_id_async(module_id)
            if name is not None:
                updated.name = name
            if description is not None:
                updated.description = description
            if status is not None:
                updated.entity_status = status
            if default_version is not None:
                updated.default_version = default_version
            if versions is not None:
                updated.versions = versions

            entity = self._service_caller.update_azure_ml_module_async(module_id, updated)
            return self.from_azure_ml_module_entity(entity, self._workspace, self,
                                                    self._module_version_provider)


class _AevaMlModuleVersionProvider(_AzureMLModuleVersionProvider):
    """
    _AevaMlModuleVersionProvider.
    """
    def __init__(self, service_caller, workspace, module_uploader):
            """Initialize _AzureMLModuleProvider.

            :param service_caller: service caller object
            :type service_caller: ServiceCaller
            :param workspace: workspace object
            :type workspace: Workspace
            :param module_uploader: module uploader object
            :type module_uploader: _AevaModuleSnapshotUploader
            """
            self._service_caller = service_caller
            self._workspace = workspace
            self._module_uploader = module_uploader

    @staticmethod
    def from_azure_ml_module_version_entity(workspace, azure_ml_module_version_entity,
                                            azure_ml_module_version_provider,
                                            version):
        """ Returns a Module.
        :param workspace: Workspace object this Mdule will belong to.
        :type workspace: azureml.core.Workspace
        :param azure_ml_module_version_entity: AzureMLModuleVersion entity
        :type azure_ml_module_version_entity: AzureMLModuleVersion
        :param azure_ml_module_version_provider: The ModuleVersion provider.
        :type azure_ml_module_version_provider: _AevaMlModuleVersionProvider
        :param version: The version.
        :type version: str
        """
        result = ModuleVersion(workspace=workspace,
                               module_entity=azure_ml_module_version_entity,
                               module_version_provider=azure_ml_module_version_provider,
                               version=version)
        return result

    def create_module_version(self, workspace, aml_module_id, version_num, module_def, content_path=None,
                              fingerprint=None):
        """Creates and returns moduleVersion.

        :param workspace: Workspace object this Mdule will belong to.
        :type workspace: azureml.core.Workspace
        :param aml_module_id: The ID of the containing module
        :param version_num: The version.
        :type version_num: str
        :type aml_module_id: str
        :param module_def: module def
        :type module_def: ModuleDef
        :param content_path: directory
        :type content_path: str
        :param fingerprint: fingerprint
        :type fingerprint: str
        """

        def creation_fn(structured_interface, storage_id, is_interface_only):
            creation_info = AzureMLModuleVersionCreationInfo(aml_module_id=aml_module_id,
                                                             version=version_num,
                                                             name=module_def.name,
                                                             description=module_def.description,
                                                             is_deterministic=module_def.allow_reuse,
                                                             module_execution_type=module_def.module_execution_type,
                                                             structured_interface=structured_interface,
                                                             identifier_hash=fingerprint,
                                                             storage_id=storage_id,
                                                             is_interface_only=is_interface_only)
            return self._service_caller.create_azure_ml_module_version_async(creation_info=creation_info)

        module_version_entity = _AevaModuleProvider.module_creation(module_def, content_path,
                                                                    self._service_caller.get_all_datatypes_async(),
                                                                    self._module_uploader, creation_fn)
        return self.from_azure_ml_module_version_entity(workspace, module_version_entity, self, version_num)

    def get_module_version(self, workspace, module_version_id):
        """Get ModuleVersion

        :param workspace: Workspace object this Mdule will belong to.
        :type workspace: azureml.core.Workspace
        :param module_version_id: The Module version id
        :type module_version_id: str
        :return: an object of :class:`azureml.pipeline.core.ModuleVersion`
        :rtype:
        :class:`azureml.pipeline.core.ModuleVersion`
        """
        entity = self._service_caller.get_azure_ml_module_version_async(azure_ml_module_version_id=module_version_id)
        module = self._service_caller.get_azure_ml_module_by_id_async(entity.module_id)
        descriptor = next((item for item in module.versions if item.module_version_id == module_version_id), None)
        return self.from_azure_ml_module_version_entity(workspace, entity, self, descriptor.version)

    def update_module_version(self, module_version_id, version, status=None, description=None):
        """Update ModuleVersion

        :param module_version_id: The Module id
        :type module_version_id: str
        :param version: The version.
        :type version: str
        :param status: The new status of Module.
        :type status: str
        :param description: The description of Module
        :type description: str
        """
        updated = self._service_caller.get_azure_ml_module_version_async(module_version_id)
        if description is not None:
            updated.data.description = description
        if status is not None:
            updated.data.entity_status = status

        self._service_caller.update_azure_ml_module_version_async(module_version_id, updated)
