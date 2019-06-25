# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DatasetActionRun module manages the Dataset actions execution.

This module provides convenient methods for creating actions and get the result after completion.
"""


class DatasetActionRun(object):
    """DatasetActionRun class manages the Dataset actions execution.

    This class provides methods for monitoring the status of long running actions
    on datasets. It also provides a method to get the result of an action after completion.
    """

    # the auth token received from _auth.get_authentication_header is prefixed
    # with 'Bearer '. This is used to remove that prefix.
    _bearer_prefix_len = 7

    def __init__(self, workspace=None, dataset_id=None, action_id=None, action_request_dto=None):
        """Initialize a DatasetActionRun.

        :param workspace: The workspace
        :type workspace: azureml.core.Workspace
        :param dataset_id: The Dataset id
        :type dataset_id: str
        :param action_id: The Dataset action id
        :type action_id: str
        :param action_request_dto: Action request dto
        :type action_request_dto: azureml._restclient.models.action_result_dto
        """
        self._workspace = workspace
        self._dataset_id = dataset_id
        self._action_id = action_id
        self._action_request_dto = action_request_dto
        self._result = None

    def wait_for_completion(self, show_output=True, status_update_frequency=10):
        """Wait for the completion of Dataset action run.

        .. remarks::

           This is a synchronous method. Call this if you have triggered a long running action on a dataset,
           and want to wait for the action to complete before proceeding. This method logs the status of the
           action run in the logs periodically, with the interval between logs determined by the
           status_update_frequency parameter.

           The action returns when the action has completed. To inspect the result of the action, use
            :func: get_result.

        :param show_output: If True the method will print the output, optional
        :type show_output: bool
        :param status_update_frequency: Action run status update frequency in seconds, optional
        :type status_update_frequency: int
        """
        if self._result is not None:
            return
        DatasetActionRun._client()._wait_for_completion(
            workspace=self._workspace,
            dataset_id=self._dataset_id,
            action_id=self._action_id,
            show_output=show_output,
            status_update_frequency=status_update_frequency)

    def get_result(self):
        """Get the result of completed Dataset action run.

        :return: Dataset action result
        :rtype: DataProfile or None
        """
        if self._result is not None:
            return self._result

        if self._action_request_dto.action_type == 'profile':
            return DatasetActionRun._client()._get_profile(
                workspace=self._workspace,
                dataset_id=self._dataset_id,
                action_id=self._action_id)
        elif self._action_request_dto.action_type == 'diff':
            return DatasetActionRun._client()._get_profile_diff_result(
                workspace=self._workspace,
                action_id=self._action_id,
                dataset_id=self._dataset_id,
                action_request_dto=self._action_request_dto)
        else:
            return None

    @staticmethod
    def _client():
        """Get a Dataset client.

        :return: Returns the client
        :rtype: DatasetClient
        """
        from ._dataset_client import _DatasetClient
        return _DatasetClient
