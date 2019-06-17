# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Access jasmineclient"""
from .experiment_client import ExperimentClient


class JasmineClient(ExperimentClient):
    """
    Jasmine APIs

    :param host: The base path for the server to call.
    :type host: str
    :param auth: Client authentication
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :type subscription_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param workspace_name:
    :type workspace_name: str
    :param project_name:
    :type project_name: str
    """
    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        return self._service_context._get_jasmine_restclient(user_agent=user_agent)

    def post_parent_run(self, create_parent_run_dto=None):
        """
        Post a new parent run to Jasmine
        :param create_parent_run_dto:
        :return:
        """
        return self._execute_with_experiment_arguments(
            self._client.jasmine.create_parent_run, create_parent_run_dto)

    def post_remote_jasmine_run(self, parent_run_id, jsondefinition, zipfile):
        """
        Post a new experiment to Jasmine
        :param parent_run_id: str
        :param jsondefinition: json str containing run configuration information
        :param zipfile: file pointer to a zipfile containing AzureML project
        :return:
        """
        return self._execute_with_experiment_arguments(
            self._client.jasmine.post_remote_run, parent_run_id, jsondefinition, zipfile)

    def post_remote_jasmine_snapshot_run(self, parent_run_id, jsondefinition, snapshotId):
        """
        Post a new experiment to Jasmine
        :param parent_run_id: str
        :param jsondefinition: json str containing run configuration information
        :param snapshotId: Id of the snapshot containing the project files
        :return:
        """
        return self._execute_with_experiment_arguments(
            self._client.jasmine.post_remote_snapshot_run, parent_run_id, jsondefinition, snapshotId)

    def get_next_task(self, parent_run_id):
        """
        Get task for next iteration to run from Jasmine
        :param parent_run_id: str
        :param worker_id: str
        :return:
        """
        dto = self._execute_with_experiment_arguments(
            self._client.jasmine.local_run_get_next_task, parent_run_id)
        return dto if dto.__dict__ is not None else None

    def get_next_pipeline(self, parent_run_id, worker_id):
            """
            Get next set of pipelines to run from Jasmine
            :param parent_run_id: str
            :param worker_id: str
            :return:
            """
            dto = self._execute_with_experiment_arguments(
                self._client.jasmine.get_pipeline, parent_run_id, worker_id)
            return dto if dto.__dict__ is not None else None

    def set_parent_run_status(self, parent_run_id, target_status):
        """
        Post a new experiment to Jasmine
        :param parent_run_id: str
        :param target_status: str
        :return:
        """
        return self._execute_with_experiment_arguments(
            self._client.jasmine.parent_run_status,
            parent_run_id, target_status)

    def cancel_child_run(self, child_run_id):
        """
        Post a new experiment to Jasmine
        :param child_run_id: str
        :return:
        """
        return self._execute_with_experiment_arguments(
            self._client.jasmine.cancel_child_run,
            child_run_id)

    def continue_remote_run(self, run_id, iterations=None, exit_time_sec=None, exit_score=None):
        """
        Post a new experiment to Jasmine
        :param child_run_id: str
        :return:
        """
        return self._execute_with_experiment_arguments(
            self._client.jasmine.continue_run,
            run_id, iterations, exit_time_sec, exit_score)
