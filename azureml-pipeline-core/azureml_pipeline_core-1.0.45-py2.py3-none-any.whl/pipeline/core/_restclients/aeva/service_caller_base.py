# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""service_calller_base.py, module for interacting with the AzureML service."""

from abc import abstractmethod, ABCMeta


class AE3PServiceCallerBase(object):
    """Handles interactions with the AzureML service for
    creating/updating datasources/modules, and submitting
    pipeline runs.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_datasource_async(self, creation_info):
        """CreateDataSourceAsync.

        :param creation_info: The datasource creation info
        :type creation_info: ~swaggerfixed.models.DataSourceCreationInfo
        :return: DatasetEntity
        :rtype: ~swaggerfixed.models.DatasetEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def update_datasource_async(self, id, updated):
        """UpdateDataSourceAsync.

        :param id: The datasource id
        :type id: str
        :param updated: The updated datasource
        :type updated: ~swaggerfixed.models.DataSourceEntity
        :return: None
        :rtype: None
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_datasource_async(self, id):
        """GetDataSourceAsync.

        :param id: The datasource id
        :type id: str
        :return: DatasetEntity
        :rtype: ~swaggerfixed.models.DatasetEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_module_async(self, id):
        """GetModuleAsync.

        :param id: The module id
        :type id: str
        :return: Module
        :rtype: ~swaggerfixed.models.Module
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def create_module_async(self, creation_info):
        """CreateModuleAsync.

        :param creation_info: The module creation info
        :type creation_info: ~swaggerfixed.models.ModuleCreationInfo
        :return: ModuleEntity
        :rtype: ~swaggerfixed.models.ModuleEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def update_module_async(self, id, updated):
        """UpdateModuleAsync.

        :param id: The module id
        :type id: str
        :param updated: The updated module
        :type updated: ~swaggerfixed.models.ModuleEntity
        :return: None
        :rtype: None
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def create_unsubmitted_pipeline_run_async(self, creation_info_with_graph, experiment_name):
        """CreateUnsubmittedPipelineRunWithGraphAsync.

        :param creation_info_with_graph: The pipeline run creation info
        :type creation_info_with_graph:
         ~swaggerfixed.models.PipelineRunCreationInfoWithGraph
        :param experiment_name: The experiment name
        :type experiment_name: str
        :return: PipelineRunEntity
        :rtype: ~swaggerfixed.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def submit_saved_pipeline_run_async(self, pipeline_run_id, parent_run_id=None):
        """SubmitSavedPipelineRunAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        :return: None
        :rtype: None
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_pipeline_run_async(self, pipeline_run_id):
        """GetPipelineRunAsync.

        :param pipeline_run_id: The PipelineRun id
        :type pipeline_run_id: str
        :return: PipelineRunEntity
        :rtype: ~swaggerfixed.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def cancel_pipeline_run_async(self, pipeline_run_id):
        """CencelPipelineRunAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :return: None
        :rtype: None
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_graph_async(self, graph_id):
        """GetGraphAsync

        :param graph_id: The graph id
        :type graph_id: str
        :return: GraphEntity
        :rtype: ~swaggerfixed.models.GraphEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_graph_interface_async(self, graph_id):
        """GetGraphInterfaceAsync

        :param graph_id: The graph id
        :type graph_id: str
        :return: GraphEntity
        :rtype: ~swaggerfixed.models.EntityInterface
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_node_status_code_async(self, pipeline_run_id, node_id):
        """GetNodeStatusCodeAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param node_id: The node id
        :type node_id: str
        :return: node status code
        :rtype: StatusCode
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_node_status_async(self, pipeline_run_id, node_id):
        """GetNodeStatusAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param node_id: The node id
        :type node_id: str
        :return: node status
        :rtype: TaskStatus
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_all_nodes_in_level_status_async(self, pipeline_run_id):
        """GetAllNodesInLevelStatusAsync.

        :param pipeline_run_id: The pipelin run id
        :type pipeline_run_id: str
        :return: dict
        :rtype: dict[str: TaskStatus]
        """
        pass

    @abstractmethod
    def get_node_outputs_async(self, pipeline_run_id, node_id):
        """GetNodeOutputsAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param node_id: The node id
        :type node_id: str
        :return: node outputs dictionary
        :rtype: dict
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_pipeline_run_output_async(self, pipeline_run_id, pipeline_run_output_name):
        """GetPipelineRunOutputAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param pipeline_run_output_name: The pipeline run output name
        :type pipeline_run_output_name: str
        :return: node output
        :rtype: NodeOutput
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_node_job_log_async(self, pipeline_run_id, node_id):
        """GetNodeJobLogAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param node_id: The node id
        :type node_id: str
        :return: node job log
        :rtype: str
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_node_stdout_log_async(self, pipeline_run_id, node_id):
        """GetNodeStdOutAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param node_id: The node id
        :type node_id: str
        :return: node stdout
        :rtype: str
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_node_stderr_log_async(self, pipeline_run_id, node_id):
        """GetNodeStdErrAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :param node_id: The node id
        :type node_id: str
        :return: node stderr
        :rtype: str
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def create_pipeline_async(self, pipeline_creation_info):
        """CreatePipelineAsync.

        :param pipeline_creation_info: The pipeline creation info
        :type pipeline_creation_info: ~swagger.models.PipelineCreationInfo
        :return: TemplateEntity
        :rtype: ~swaggerfixed.models.PipelineEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_pipeline_async(self, pipeline_id):
        """GetPipelineAsync.

        :param pipeline_id: The pipeline id
        :type pipeline_id: str
        :return: TemplateEntity
        :rtype: ~swaggerfixed.models.PipelineEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def submit_pipeline_run_from_pipeline_async(self, pipeline_id, pipeline_submission_info, parent_run_id=None):
        """SubmitPipelineRunFromPipelineAsync.

        :param pipeline_id: The pipeline id
        :type pipeline_id: str
        :param pipeline_submission_info: pipeline submission information
        :type pipeline_submission_info: ~swagger.models.PipelineSubmissionInfo
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        :return: PipelineRunEntity
        :rtype: ~swaggerfixed.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def try_get_module_by_hash_async(self, identifier_hash):
        """GetModuleByHashAsync.

        :param identifier_hash: The module identifierHash
        :type identifier_hash: str
        :return: Module that was found, or None if not found
        :rtype: ~swagger.models.Module
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        pass

    @abstractmethod
    def try_get_datasource_by_hash_async(self, identifier_hash):
        """GetDataSourceByHashAsync.

        :param identifier_hash: The datasource identifierHash
        :type identifier_hash: str
        :return: DataSourceEntity that was found, or None if not found
        :rtype: ~swagger.models.DataSourceEntity or
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        pass

    @abstractmethod
    def get_all_datatypes_async(self):
        """GetAllDataTypesAsync.

        :return: list
        :rtype: list[~swagger.models.DataTypeEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def create_datatype_async(self, creation_info):
        """CreateNewDataTypeAsync.

        :param creation_info: The DataTypeEntity creation info
        :type creation_info: ~swagger.models.DataTypeCreationInfo
        :return: DataTypeEntity
        :rtype: ~swagger.models.DataTypeEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def update_datatype_async(self, id, updated):
        """UpdateDataTypeAsync.

        :param id: The DataTypeEntity id
        :type id: str
        :param updated: The DataTypeEntity to update
        :type updated: ~swagger.models.DataTypeEntity
        :return: DataTypeEntity
        :rtype: ~swagger.models.DataTypeEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_pipeline_runs_by_pipeline_id_async(self, pipeline_id):
        """GetPipelineRunsByPipelineIdAsync.

        :param pipeline_id: The published pipeline id
        :type pipeline_id: str
        :return: list
        :rtype: list[~swagger.models.PipelineRunEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @abstractmethod
    def get_all_published_pipelines(self, active_only=True):
        """GetPublishedPipelinesAsync.

        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.TemplateEntity]
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        pass

    @abstractmethod
    def update_published_pipeline_status_async(self, pipeline_id, new_status):
        """UpdateStatusAsync.

        :param pipeline_id: The published pipeline id
        :type pipeline_id: str
        :param new_status: New status for the template ('Active', 'Deprecated', or 'Disabled')
        :type new_status: str
        :return: None
        :rtype: None
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def create_schedule_async(self, schedule_creation_info):
        """CreateScheduleAsync.

        :param schedule_creation_info: The schedule creation info
        :type schedule_creation_info: ~swagger.models.ScheduleCreationInfo
        :return: PipelineScheduleEntity
        :rtype: ~swagger.models.PipelineScheduleEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_schedule_async(self, schedule_id):
        """GetScheduleAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return: PipelineScheduleEntity
        :rtype: ~swaggerfixed.models.PipelineScheduleEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def update_schedule_async(self, schedule_id, updated):
        """UpdateScheduleAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :param updated: The Schedule
        :type updated: ~swagger.models.PipelineScheduleEntity
        :return: PipelineScheduleEntity
        :rtype: ~swagger.models.PipelineScheduleEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_all_schedules_async(self, active_only):
        """GetSchedulesAsync.

        :param active_only: True to return only active schedules
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.PipelineScheduleEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_schedules_by_pipeline_id_async(self, pipeline_id):
        """GetSchedulesByPipelineIdAsync.

        :param pipeline_id: The published pipeline id
        :type pipeline_id: str
        :return: list
        :rtype: list[~swagger.models.PipelineScheduleEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_pipeline_runs_by_schedule_id_async(self, schedule_id):
        """GetPipelineRunsByScheduleIdAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return: list
        :rtype: list[~swagger.models.PipelineRunEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_last_pipeline_run_by_schedule_id_async(self, schedule_id):
        """GetLastPipelineRunByScheduleIdAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return: PipelineRunEntity
        :rtype: ~swagger.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    @staticmethod
    def entity_status_from_enum(status_enum):
        """Convert an enum entity status from the Aeva backend to a string

        :param status_enum: Entity status as from the Aeva enum ('0', '1', or '2')
        :type status_enum: str
        :return: Status value ('Active', 'Deprecated', or 'Disabled')
        :rtype: str
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if status_enum == '0':
            return 'Active'
        elif status_enum == '1':
            return 'Deprecated'
        elif status_enum == '2':
            return 'Disabled'
        else:
            return status_enum

    @staticmethod
    def entity_status_to_enum(status):
        """Convert a string entity status to the Aeva backend enum

        :param status: Status value ('Active', 'Deprecated', or 'Disabled')
        :type status: str
        :return: Entity status as from the Aeva enum ('0', '1', or '2')
        :rtype: str
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if status == 'Active':
            return '0'
        elif status == 'Deprecated':
            return '1'
        elif status == 'Disabled':
            return '2'
        else:
            raise ValueError("Invalid entity status " + status)

    @staticmethod
    def frequency_to_enum(frequency):
        """Convert a string frequency to the Aeva backend enum

        :param frequency: Frequency value ('Month', 'Week', 'Day', 'Hour',  or 'Minute')
        :type frequency: str
        :return: Entity status as from the Aeva enum ('0', '1', '2', '3' or '4')
        :rtype: str
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if frequency == 'Month':
            return '0'
        elif frequency == 'Week':
            return '1'
        elif frequency == 'Day':
            return '2'
        elif frequency == 'Hour':
            return '3'
        elif frequency == 'Minute':
            return '4'
        else:
            raise ValueError("Invalid entity status " + frequency)

    @staticmethod
    def frequency_from_enum(frequency_enum):
        """Convert an enum frequency from the Aeva backend to a string

        :param frequency_enum: Entity status as from the Aeva enum ('0', '1', '2', '3' or '4')
        :type frequency_enum: str
        :return: Frequency value ('Month', 'Week', 'Day', 'Hour',  or 'Minute')
        :rtype: str
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if frequency_enum == '0':
            return 'Month'
        elif frequency_enum == '1':
            return 'Week'
        elif frequency_enum == '2':
            return 'Day'
        elif frequency_enum == '3':
            return 'Hour'
        elif frequency_enum == '4':
            return 'Minute'
        else:
            return frequency_enum

    @staticmethod
    def week_days_to_enum(week_days):
        """Convert a string week day to the Aeva backend enum

        :param week_days: Week day value ('Monday'-'Sunday')
        :type week_days: list
        :return: Entity status as from the Aeva enum ('0'-'6')
        :rtype: list
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if week_days is None:
            return None
        new_week_days = []
        for week_day in week_days:
            if week_day == 'Monday':
                new_week_days.append('0')
            elif week_day == 'Tuesday':
                new_week_days.append('1')
            elif week_day == 'Wednesday':
                new_week_days.append('2')
            elif week_day == 'Thursday':
                new_week_days.append('3')
            elif week_day == 'Friday':
                new_week_days.append('4')
            elif week_day == 'Saturday':
                new_week_days.append('5')
            elif week_day == 'Sunday':
                new_week_days.append('6')
            else:
                raise ValueError("Invalid week day " + week_day)
        return new_week_days

    @staticmethod
    def week_days_from_enum(week_days_enum):
        """Convert an enum week day from the Aeva backend to a string

        :param week_days_enum: Entity status as from the Aeva enum ('0'-'6')
        :type week_days_enum: list
        :return: Week day value ('Monday'-'Sunday')
        :rtype: list
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if week_days_enum is None:
            return None
        new_week_days = []
        for week_day in week_days_enum:
            if week_day == '0':
                new_week_days.append('Monday')
            elif week_day == '1':
                new_week_days.append('Tuesday')
            elif week_day == '2':
                new_week_days.append('Wednesday')
            elif week_day == '3':
                new_week_days.append('Thursday')
            elif week_day == '4':
                new_week_days.append('Friday')
            elif week_day == '5':
                new_week_days.append('Saturday')
            elif week_day == '6':
                new_week_days.append('Sunday')
            else:
                new_week_days.append(week_day)
        return new_week_days

    @staticmethod
    def provisioning_status_from_enum(provisioning_status_enum):
        """Convert an enum provisioning status from the Aeva backend to a string

        :param provisioning_status_enum: Provisioning status as from the Aeva enum ('0', '1', '2')
        :type provisioning_status_enum: str
        :return: Provisioning status value ('Completed', 'Provisioning', or 'Failed')
        :rtype: str
        """
        # TODO: The backend is switching from returning an int status code to a string status code
        # After this is complete, we can remove the code that converts the int values
        if provisioning_status_enum == '0':
            return 'Completed'
        elif provisioning_status_enum == '1':
            return 'Provisioning'
        elif provisioning_status_enum == '2':
            return 'Failed'
        else:
            return provisioning_status_enum

    def create_pipeline_endpoint_async(self, pipeline_endpoint_creation_info):
        """CreatePipelineEndpointAsync.

        :param pipeline_endpoint_creation_info: The pipeline_endpoint creation info
        :type pipeline_endpoint_creation_info: ~swagger.models.PipelineEndpointCreationInfo
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_pipeline_endpoint_by_id_async(self, endpoint_id=None):
        """GetPipelineEndpointByIdAsync.

        :param endpoint_id: Id of PipelineEndpoint
        :type endpoint_id: str
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_pipeline_endpoint_by_name_async(self, name=None):
        """GetPipelineEndpointByNameAsync.

        :param name: Name of PipelineEndpoint
        :type name: str
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def update_pipeline_endpoint_async(self, endpoint_id, updated):
        """UpdatePipelineEndpointAsync.

        :param endpoint_id: The PipelineEndpoint id
        :type endpoint_id: str
        :param updated: The PipelineEndpointEntity
        :type updated: ~swagger.models.PipelineEndpointEntity
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_all_pipeline_endpoints_async(self, active_only=True):
        """GetPipelineEndpointsAsync.

        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.PipelineEndpointEntity]
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        pass

    def create_azure_ml_module_async(self, azure_ml_module_creation_info):
        """CreateAzureMLModuleAsync.

        :param azure_ml_module_creation_info: The azureML_Module creation info
        :type azure_ml_module_creation_info: ~swagger.models.AzureMLModuleCreationInfo
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_azure_ml_module_by_id_async(self, azure_ml_module_id=None):
        """GetAzureMLModuleByIdAsync.

        :param azure_ml_module_id: Id of AzureMLModule
        :type azure_ml_module_id: str
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_azure_ml_module_by_name_async(self, name=None):
        """GetAzureMLModuleByNameAsync.

        :param name: Name of AzureMLModule
        :type name: str
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def update_azure_ml_module_async(self, azure_ml_module_id, updated):
        """UpdateAzureMLModuleAsync.

        :param azure_ml_module_id: The Module id
        :type azure_ml_module_id: str
        :param updated: The AzureMLModule
        :type updated: ~swagger.models.AzureMLModule
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def create_azure_ml_module_version_async(self, azure_ml_module_version_creation_info):
        """CreateAzureMLModuleAsync.

        :param azure_ml_module_version_creation_info: The azureML_module_version creation info
        :type azure_ml_module_version_creation_info: ~swagger.models.AzureMLModuleVersionCreationInfo
        :return: AzureMLModuleVersion
        :rtype: ~swagger.models.AzureMLModuleVersion
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_azure_ml_module_version_by_id_async(self, azure_ml_module_version_id=None):
        """GetAzureMLModuleVersionByIdAsync.

        :param azure_ml_module_version_id: Id of AzureMLModule
        :type azure_ml_module_version_id: str
        :return: AzureMLModuleVersion
        :rtype: ~swagger.models.AzureMLModuleVersion
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def update_azure_ml_module_version_async(self, azure_ml_module_version_id, updated):
        """UpdateAzureMLModuleVersionAsync.

        :param azure_ml_module_version_id: The Module id
        :type azure_ml_module_version_id: str
        :param updated: The AzureMLModuleVersion
        :type updated: ~swagger.models.AzureMLModuleVersion
        :return: AzureMLModuleVersion
        :rtype: ~swagger.models.AzureMLModuleVersion
        :raises:
         :class:`ErrorResponseException`
        """
        pass

    def get_all_pipelines_from_pipeline_endpoint_async(self, endpoint_id, active_only=True):
        """GetPipelinesAsync.

        :param endpoint_id: The pipeline endpoint id
        :type endpoint_id: str
        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.PipelineEntity]
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        pass
