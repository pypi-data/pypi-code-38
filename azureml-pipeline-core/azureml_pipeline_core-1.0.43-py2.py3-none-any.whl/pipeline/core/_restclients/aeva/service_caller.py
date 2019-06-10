# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""service_calller.py, module for interacting with the AzureML service."""

from .aml_pipelines_api10 import AMLPipelinesAPI10
from .service_caller_base import AE3PServiceCallerBase
from .models import ErrorResponseException


class AE3PServiceCaller(AE3PServiceCallerBase):
    """AE3PServiceCaller.
    :param base_url: base url
    :type base_url: Service URL
    :param workspace: workspace
    :type workspace: Workspace
    """
    def __init__(self, base_url, workspace):
        """Initializes AE3PServiceCaller."""
        self._service_endpoint = base_url
        self._caller = AMLPipelinesAPI10(base_url=base_url)
        self._subscription_id = workspace.subscription_id
        self._resource_group_name = workspace.resource_group
        self._workspace_name = workspace.name
        self.auth = workspace._auth_object
        self.data_types_cache = []

    def _get_custom_headers(self):
        return self.auth.get_authentication_header()

    def create_datasource_async(self, creation_info):
        """CreateDataSourceAsync.

        :param creation_info: The datasource creation info
        :type creation_info: ~swaggerfixed.models.DataSourceCreationInfo
        :return: DatasetEntity
        :rtype: ~swaggerfixed.models.DatasetEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_sources_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), creation_info=creation_info)

        return result

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

        self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_sources_by_data_source_id_put(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            data_source_id=id, updated=updated)

    def get_datasource_async(self, id):
        """GetDataSourceAsync.

        :param id: The datasource id
        :type id: str
        :return: DatasetEntity
        :rtype: ~swaggerfixed.models.DatasetEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_sources_by_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            id=id)

        return result

    def get_module_async(self, id):
        """GetModuleAsync.

        :param id: The module id
        :type id: str
        :return: Module
        :rtype: ~swaggerfixed.models.Module
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_modules_by_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), id=id)

        return result

    def create_module_async(self, creation_info):
        """CreateModuleAsync.

        :param creation_info: The module creation info
        :type creation_info: ~swaggerfixed.models.ModuleCreationInfo
        :return: ModuleEntity
        :rtype: ~swaggerfixed.models.ModuleEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_modules_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), creation_info=creation_info)

        return result

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

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_modules_by_id_put(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, id=id, updated=updated, custom_headers=self._get_custom_headers())

        return result

    def create_unsubmitted_pipeline_run_async(self, creation_info_with_graph, experiment_name):
        """CreateUnsubmittedPipelineRunWithGraphAsync.

        :param creation_info_with_graph: The pipeline run creation info
        :type creation_info_with_graph:
        :param experiment_name: The experiment name
        :type experiment_name: str
         ~swaggerfixed.models.PipelineRunCreationInfoWithGraph
        :return: PipelineRunEntity
        :rtype: ~swaggerfixed.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_unsubmitted_creation_info_with_graph_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            creation_info_with_graph=creation_info_with_graph, experiment_name=experiment_name)

        return result

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

        self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_submit_by_pipeline_run_id_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), pipeline_run_id=pipeline_run_id, parent_run_id=parent_run_id)

    def get_pipeline_run_async(self, pipeline_run_id):
        """GetPipelineRunAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :return: PipelineRunEntity
        :rtype: ~swaggerfixed.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), pipeline_run_id=pipeline_run_id)

        return result

    def cancel_pipeline_run_async(self, pipeline_run_id):
        """CancelPipelineRunAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :return: None
        :rtype: None
        :raises:
         :class:`ErrorResponseException`
        """
        self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_execution_delete(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, custom_headers=self._get_custom_headers())

    def get_graph_async(self, graph_id):
        """GetGraphAsync

        :param graph_id: The graph id
        :type graph_id: str
        :return: GraphEntity
        :rtype: ~swaggerfixed.models.GraphEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_graphs_by_graph_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, graph_id=graph_id, custom_headers=self._get_custom_headers())

        return result

    def get_graph_interface_async(self, graph_id):
        """GetGraphInterfaceAsync

        :param graph_id: The graph id
        :type graph_id: str
        :return: GraphEntity
        :rtype: ~swaggerfixed.models.EntityInterface
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_graphs_by_graph_id_interface_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, graph_id=graph_id, custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_graph_node_status_code_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[node_id],
            custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_graph_node_status_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[node_id],
            custom_headers=self._get_custom_headers())

        return result

    def get_all_nodes_in_level_status_async(self, pipeline_run_id):
        """GetAllNodesInLevelStatusAsync.

        :param pipeline_run_id: The pipeline run id
        :type pipeline_run_id: str
        :return: dict
        :rtype: dict[str: TaskStatus]
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_graph_all_nodes_status_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[],
            custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_outputs_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[node_id],
            custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.get_pipeline_run_output_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id,
            pipeline_run_output_name=pipeline_run_output_name, custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_graph_shareable_job_log_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[node_id],
            custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_graph_shareable_stdout_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[node_id],
            custom_headers=self._get_custom_headers())

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_by_pipeline_run_id_graph_shareable_stderr_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, pipeline_run_id=pipeline_run_id, node_id_path=[node_id],
            custom_headers=self._get_custom_headers())

        return result

    def create_pipeline_async(self, pipeline_creation_info):
        """CreatePipelineAsync.

        :param pipeline_creation_info: The pipeline creation info
        :type pipeline_creation_info: ~swagger.models.PipelineCreationInfo
        :return: TemplateEntity
        :rtype: ~swaggerfixed.models.PipelineEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipelines_create_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            pipeline_creation_info=pipeline_creation_info)

        return result

    def get_pipeline_async(self, pipeline_id):
        """GetPipelineAsync.

        :param pipeline_id: The pipeline id
        :type pipeline_id: str
        :return: TemplateEntity
        :rtype: ~swaggerfixed.models.PipelineEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipelines_by_pipeline_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), pipeline_id=pipeline_id)

        return result

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

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_pipeline_submit_by_pipeline_id_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            pipeline_id=pipeline_id, pipeline_submission_info=pipeline_submission_info, parent_run_id=parent_run_id)

        return result

    def try_get_module_by_hash_async(self, identifier_hash):
        """GetModuleByHashAsync.

        :param identifier_hash: The module identifierHash
        :type identifier_hash: str
        :return: Module that was found, or None if not found
        :rtype: ~swagger.models.Module
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        try:
            result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_modules_hash_by_identifier_hash_get(
                subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                custom_headers=self._get_custom_headers(),
                identifier_hash=identifier_hash)
        except ErrorResponseException:
            # If the module was not found, return None
            return None

        return result

    def try_get_datasource_by_hash_async(self, identifier_hash):
        """GetDataSourceByHashAsync.

        :param identifier_hash: The datasource identifierHash
        :type identifier_hash: str
        :return: DataSourceEntity that was found, or None if not found
        :rtype: ~swagger.models.DataSourceEntity or
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        try:
            result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_sources_hash_by_hash_get(
                subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                custom_headers=self._get_custom_headers(),
                hash=identifier_hash)
        except ErrorResponseException:
            # If the module was not found, return None
            return None

        return result

    def get_all_datatypes_async(self):
        """GetAllDataTypesAsync.

        :return: list
        :rtype: list[~swagger.models.DataTypeEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        if len(self.data_types_cache) == 0:
            result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_types_get(
                subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name, custom_headers=self._get_custom_headers())
            self.data_types_cache = result
            return result
        else:
            return self.data_types_cache

    def create_datatype_async(self, creation_info):
        """CreateNewDataTypeAsync.

        :param creation_info: The DataTypeEntity creation info
        :type creation_info: ~swagger.models.DataTypeCreationInfo
        :return: DataTypeEntity
        :rtype: ~swagger.models.DataTypeEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_types_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            creation_info=creation_info)
        self.data_types_cache = []  # clear cache
        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_data_types_by_id_put(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            id=id, updated=updated)
        self.data_types_cache = []  # clear cache
        return result

    def get_pipeline_runs_by_pipeline_id_async(self, pipeline_id):
        """GetPipelineRunsByPipelineIdAsync.

        :param pipeline_id: The published pipeline id
        :type pipeline_id: str
        :return: list
        :rtype: list[~swagger.models.PipelineRunEntity]
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_pipeline_by_pipeline_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            pipeline_id=pipeline_id)

        return result

    def get_all_published_pipelines(self, active_only=True):
        """GetPipelinesAsync.

        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.TemplateEntity]
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipelines_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            active_only=active_only)

        return result

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
        self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipelines_by_pipeline_id_status_put(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            pipeline_id=pipeline_id, new_status=new_status)

    def create_schedule_async(self, schedule_creation_info):
        """CreateScheduleAsync.

        :param schedule_creation_info: The schedule creation info
        :type schedule_creation_info: ~swagger.models.ScheduleCreationInfo
        :return: PipelineScheduleEntity
        :rtype: ~swagger.models.PipelineScheduleEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_schedules_create_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            schedule_creation_info=schedule_creation_info)

        return result

    def get_schedule_async(self, schedule_id):
        """GetScheduleAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return: PipelineScheduleEntity
        :rtype: ~swaggerfixed.models.PipelineScheduleEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_schedules_by_schedule_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), schedule_id=schedule_id)

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_schedules_by_schedule_id_put(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            schedule_id=schedule_id, updated=updated)

        return result

    def get_all_schedules_async(self, active_only):
        """GetSchedulesAsync.

        :param active_only: True to return only active schedules
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.PipelineScheduleEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_schedules_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), active_only=active_only)

        return result

    def get_schedules_by_pipeline_id_async(self, pipeline_id):
        """GetSchedulesByPipelineIdAsync.

        :param pipeline_id: The published pipeline id
        :type pipeline_id: str
        :return: list
        :rtype: list[~swagger.models.PipelineScheduleEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_schedules_pipeline_by_pipeline_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), pipeline_id=pipeline_id)

        return result

    def get_pipeline_runs_by_schedule_id_async(self, schedule_id):
        """GetPipelineRunsByScheduleIdAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return: list
        :rtype: list[~swagger.models.PipelineRunEntity]
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_schedule_by_schedule_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), schedule_id=schedule_id)

        return result

    def get_last_pipeline_run_by_schedule_id_async(self, schedule_id):
        """GetLastPipelineRunByScheduleIdAsync.

        :param schedule_id: The schedule id
        :type schedule_id: str
        :return: PipelineRunEntity
        :rtype: ~swagger.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_runs_schedule_by_schedule_id_last_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), schedule_id=schedule_id)

        return result

    def create_pipeline_endpoint_async(self, pipeline_endpoint_creation_info):
        """CreatePipelineEndpointAsync.

        :param pipeline_endpoint_creation_info: The pipeline_endpoint creation info
        :type pipeline_endpoint_creation_info: ~swagger.models.PipelineEndpointCreationInfo
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoint_create_post(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            pipeline_endpoint_creation_info=pipeline_endpoint_creation_info)

        return result

    def get_pipeline_endpoint_by_id_async(self, endpoint_id=None):
        """GetPipelineEndpointByIdAsync.

        :param endpoint_id: Id of PipelineEndpoint
        :type endpoint_id: str
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoint_by_id_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            endpoint_id=endpoint_id)
        result
        return result

    def get_pipeline_endpoint_by_name_async(self, name=None):
        """GetPipelineEndpointByNameAsync.

        :param name: Name of PipelineEndpoint
        :type name: str
        :return: PipelineEndpointEntity
        :rtype: ~swagger.models.PipelineEndpointEntity
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoint_by_name_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            name=name)
        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoint_by_id_put(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, endpoint_id=endpoint_id, custom_headers=self._get_custom_headers(),
            updated=updated)

        return result

    def get_all_pipeline_endpoints_async(self, active_only=True):
        """GetPipelineEndpointsAsync.

        :param active_only: Indicate whether to load active only
        :type active_only: bool
        :return: list
        :rtype: list[~swagger.models.PipelineEndpointEntity]
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoints_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            active_only=active_only)

        return result

    def submit_pipeline_run_from_pipeline_endpoint_async(self, endpoint_id, pipeline_submission_info,
                                                         parent_run_id=None, pipeline_version=None):
        """SubmitPipelineRunFromPipelineEndpointAsync.

        :param endpoint_id: The pipeline id
        :type endpoint_id: str
        :param pipeline_submission_info: pipeline submission information
        :type pipeline_submission_info: ~swagger.models.PipelineSubmissionInfo
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        :return: PipelineRunEntity
        :param pipeline_version: The pipeline version
        :type pipeline_version: str
        :rtype: ~swaggerfixed.models.PipelineRunEntity
        :raises:
         :class:`ErrorResponseException`
        """

        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_groups_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoint_submit_by_pipeline_run_id_post(
            id=endpoint_id, subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            endpoint_id=endpoint_id, pipeline_submission_info=pipeline_submission_info, parent_run_id=parent_run_id,
            pipeline_version=pipeline_version)

        return result

    def create_azure_ml_module_async(self, azure_ml_module_creation_info):
        """CreateAzureMLModuleAsync.

        :param azure_ml_module_creation_info: The azureML_Module creation info
        :type azure_ml_module_creation_info: ~swagger.models.AzureMLModuleCreationInfo
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.create_azure_ml_module_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            creation_info=azure_ml_module_creation_info)

        return result

    def get_azure_ml_module_by_id_async(self, azure_ml_module_id=None):
        """GetAzureMLModuleByIdAsync.

        :param azure_ml_module_id: Id of AzureMLModule
        :type azure_ml_module_id: str
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.get_azure_ml_module_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            id=azure_ml_module_id)

        return result

    def get_azure_ml_module_by_name_async(self, name=None):
        """GetAzureMLModuleByNameAsync.

        :param name: Name of AzureMLModule
        :type name: str
        :return: AzureMLModule
        :rtype: ~swagger.models.AzureMLModule
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.get_azure_ml_module_by_name_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            name=name)
        return result

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
        result = self._caller.update_azure_ml_module_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, id=azure_ml_module_id, custom_headers=self._get_custom_headers(),
            updated=updated)

        return result

    def create_azure_ml_module_version_async(self, creation_info):
        """CreateAzureMLModuleAsync.

        :param creation_info: The azureML_module_version creation info
        :type creation_info: ~swagger.models.AzureMLModuleVersionCreationInfo
        :return: AzureMLModuleVersion
        :rtype: ~swagger.models.AzureMLModuleVersion
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.create_azure_ml_module_version_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            creation_info=creation_info)

        return result

    def get_azure_ml_module_version_async(self, azure_ml_module_version_id=None):
        """GetAzureMLModuleVersionByIdAsync.

        :param azure_ml_module_version_id: Id of AzureMLModule
        :type azure_ml_module_version_id: str
        :return: AzureMLModuleVersion
        :rtype: ~swagger.models.AzureMLModuleVersion
        :raises:
         :class:`ErrorResponseException`
        """
        result = self._caller.get_azure_ml_module_version_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(),
            id=azure_ml_module_version_id)

        return result

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
        result = self._caller.update_azure_ml_module_version_async(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, id=azure_ml_module_version_id,
            custom_headers=self._get_custom_headers(),
            updated=updated)

        return result

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
        result = self._caller.api_v10_subscriptions_by_subscription_id_resource_group_by_resource_group_name_providers_microsoft_machine_learning_services_workspaces_by_workspace_name_pipeline_endpoints_by_id_pipelines_get(
            subscription_id=self._subscription_id, resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name, custom_headers=self._get_custom_headers(), id=endpoint_id,
            active_only=active_only)

        return result
