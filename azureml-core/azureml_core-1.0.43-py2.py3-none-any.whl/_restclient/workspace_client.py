# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------
"""Access workspace client"""
import copy

from .clientbase import ClientBase, PAGINATED_KEY

from .constants import ORDER_BY_CREATEDTIME_EXPRESSION
from .utils import _generate_client_kwargs, _validate_order_by
from .exceptions import ServiceException
from .models.error_response import ErrorResponseException


class WorkspaceClient(ClientBase):
    """
    Run History APIs

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
    """

    def __init__(self, service_context, host=None, **kwargs):
        """
        Constructor of the class.
        """
        self._service_context = service_context
        self._override_host = host
        self._workspace_arguments = [self._service_context.subscription_id,
                                     self._service_context.resource_group_name,
                                     self._service_context.workspace_name]
        super(WorkspaceClient, self).__init__(**kwargs)

        self._custom_headers = {}

    @property
    def auth(self):
        return self._service_context.get_auth()

    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        return self._service_context._get_run_history_restclient(
            host=self._override_host, user_agent=user_agent)

    def get_cluster_url(self):
        """get service url"""
        return self._host

    def get_workspace_uri_path(self):
        return self._service_context._get_workspace_scope()

    def _execute_with_workspace_arguments(self, func, *args, **kwargs):
        return self._execute_with_arguments(func, copy.deepcopy(self._workspace_arguments), *args, **kwargs)

    def _execute_with_arguments(self, func, args_list, *args, **kwargs):
        if not callable(func):
            raise TypeError('Argument is not callable')

        if self._custom_headers:
            kwargs["custom_headers"] = self._custom_headers

        if args:
            args_list.extend(args)
        is_paginated = kwargs.pop(PAGINATED_KEY, False)
        try:
            if is_paginated:
                return self._call_paginated_api(func, *args_list, **kwargs)
            else:
                return self._call_api(func, *args_list, **kwargs)
        except ErrorResponseException as e:
            raise ServiceException(e)

    def list_experiments(self, last=None, order_by=None):
        """
        list all experiments
        :return: a generator of ~_restclient.models.ExperimentDto
        """

        kwargs = {}
        if last is not None:
            order_by_expression = _validate_order_by(order_by) if order_by else [ORDER_BY_CREATEDTIME_EXPRESSION]
            kwargs = _generate_client_kwargs(top=last, orderby=order_by_expression)
            # TODO: Doesn't work
            raise NotImplementedError("Cannot limit experiment list")

        return self._execute_with_workspace_arguments(self._client.experiment.list,
                                                      is_paginated=True,
                                                      **kwargs)

    def get_experiment(self, experiment_name, is_async=False):
        """
        list all experiments in a workspace
        :return: a generator of ~_restclient.models.ExperimentDto
        :param is_async bool: execute request asynchronously
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async_task.AsyncTask object
            If parameter is_async is False or missing,
            return: ~_restclient.models.ExperimentDto
        """

        return self._execute_with_workspace_arguments(self._client.experiment.get,
                                                      experiment_name=experiment_name,
                                                      is_async=is_async)
