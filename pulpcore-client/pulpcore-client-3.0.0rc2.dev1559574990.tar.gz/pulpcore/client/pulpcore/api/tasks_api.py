# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from pulpcore.client.pulpcore.api_client import ApiClient
from pulpcore.client.pulpcore.exceptions import (
    ApiTypeError,
    ApiValueError
)


class TasksApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def tasks_cancel(self, task_href, data, **kwargs):  # noqa: E501
        """Cancel a task  # noqa: E501

        This operation cancels a task.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_cancel(task_href, data, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str task_href: URI of Task. e.g.: /pulp/api/v3/tasks/1/ (required)
        :param Task data: (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Task
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.tasks_cancel_with_http_info(task_href, data, **kwargs)  # noqa: E501

    def tasks_cancel_with_http_info(self, task_href, data, **kwargs):  # noqa: E501
        """Cancel a task  # noqa: E501

        This operation cancels a task.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_cancel_with_http_info(task_href, data, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str task_href: URI of Task. e.g.: /pulp/api/v3/tasks/1/ (required)
        :param Task data: (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(Task, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['task_href', 'data']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tasks_cancel" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'task_href' is set
        if ('task_href' not in local_var_params or
                local_var_params['task_href'] is None):
            raise ApiValueError("Missing the required parameter `task_href` when calling `tasks_cancel`")  # noqa: E501
        # verify the required parameter 'data' is set
        if ('data' not in local_var_params or
                local_var_params['data'] is None):
            raise ApiValueError("Missing the required parameter `data` when calling `tasks_cancel`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'task_href' in local_var_params:
            path_params['task_href'] = local_var_params['task_href']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'data' in local_var_params:
            body_params = local_var_params['data']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '{task_href}cancel/', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Task',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tasks_delete(self, task_href, **kwargs):  # noqa: E501
        """Delete a task  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_delete(task_href, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str task_href: URI of Task. e.g.: /pulp/api/v3/tasks/1/ (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.tasks_delete_with_http_info(task_href, **kwargs)  # noqa: E501

    def tasks_delete_with_http_info(self, task_href, **kwargs):  # noqa: E501
        """Delete a task  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_delete_with_http_info(task_href, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str task_href: URI of Task. e.g.: /pulp/api/v3/tasks/1/ (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['task_href']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tasks_delete" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'task_href' is set
        if ('task_href' not in local_var_params or
                local_var_params['task_href'] is None):
            raise ApiValueError("Missing the required parameter `task_href` when calling `tasks_delete`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'task_href' in local_var_params:
            path_params['task_href'] = local_var_params['task_href']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '{task_href}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=None,  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tasks_list(self, **kwargs):  # noqa: E501
        """List tasks  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_list(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str ordering: Which field to use when ordering the results.
        :param str state:
        :param str state__in: Filter results where state is in a comma-separated list of values
        :param str worker: Foreign Key referenced by HREF
        :param str worker__in: Filter results where worker is in a comma-separated list of values
        :param str name__contains: Filter results where name contains value
        :param str started_at__lt: Filter results where started_at is less than value
        :param str started_at__lte: Filter results where started_at is less than or equal to value
        :param str started_at__gt: Filter results where started_at is greater than value
        :param str started_at__gte: Filter results where started_at is greater than or equal to value
        :param str started_at__range: Filter results where started_at is between two comma separated values
        :param str finished_at__lt: Filter results where finished_at is less than value
        :param str finished_at__lte: Filter results where finished_at is less than or equal to value
        :param str finished_at__gt: Filter results where finished_at is greater than value
        :param str finished_at__gte: Filter results where finished_at is greater than or equal to value
        :param str finished_at__range: Filter results where finished_at is between two comma separated values
        :param str parent: Foreign Key referenced by HREF
        :param str name:
        :param str started_at: ISO 8601 formatted dates are supported
        :param str finished_at: ISO 8601 formatted dates are supported
        :param int page: A page number within the paginated result set.
        :param int page_size: Number of results to return per page.
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: InlineResponse2003
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.tasks_list_with_http_info(**kwargs)  # noqa: E501

    def tasks_list_with_http_info(self, **kwargs):  # noqa: E501
        """List tasks  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_list_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str ordering: Which field to use when ordering the results.
        :param str state:
        :param str state__in: Filter results where state is in a comma-separated list of values
        :param str worker: Foreign Key referenced by HREF
        :param str worker__in: Filter results where worker is in a comma-separated list of values
        :param str name__contains: Filter results where name contains value
        :param str started_at__lt: Filter results where started_at is less than value
        :param str started_at__lte: Filter results where started_at is less than or equal to value
        :param str started_at__gt: Filter results where started_at is greater than value
        :param str started_at__gte: Filter results where started_at is greater than or equal to value
        :param str started_at__range: Filter results where started_at is between two comma separated values
        :param str finished_at__lt: Filter results where finished_at is less than value
        :param str finished_at__lte: Filter results where finished_at is less than or equal to value
        :param str finished_at__gt: Filter results where finished_at is greater than value
        :param str finished_at__gte: Filter results where finished_at is greater than or equal to value
        :param str finished_at__range: Filter results where finished_at is between two comma separated values
        :param str parent: Foreign Key referenced by HREF
        :param str name:
        :param str started_at: ISO 8601 formatted dates are supported
        :param str finished_at: ISO 8601 formatted dates are supported
        :param int page: A page number within the paginated result set.
        :param int page_size: Number of results to return per page.
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(InlineResponse2003, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['ordering', 'state', 'state__in', 'worker', 'worker__in', 'name__contains', 'started_at__lt', 'started_at__lte', 'started_at__gt', 'started_at__gte', 'started_at__range', 'finished_at__lt', 'finished_at__lte', 'finished_at__gt', 'finished_at__gte', 'finished_at__range', 'parent', 'name', 'started_at', 'finished_at', 'page', 'page_size']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tasks_list" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'ordering' in local_var_params:
            query_params.append(('ordering', local_var_params['ordering']))  # noqa: E501
        if 'state' in local_var_params:
            query_params.append(('state', local_var_params['state']))  # noqa: E501
        if 'state__in' in local_var_params:
            query_params.append(('state__in', local_var_params['state__in']))  # noqa: E501
        if 'worker' in local_var_params:
            query_params.append(('worker', local_var_params['worker']))  # noqa: E501
        if 'worker__in' in local_var_params:
            query_params.append(('worker__in', local_var_params['worker__in']))  # noqa: E501
        if 'name__contains' in local_var_params:
            query_params.append(('name__contains', local_var_params['name__contains']))  # noqa: E501
        if 'started_at__lt' in local_var_params:
            query_params.append(('started_at__lt', local_var_params['started_at__lt']))  # noqa: E501
        if 'started_at__lte' in local_var_params:
            query_params.append(('started_at__lte', local_var_params['started_at__lte']))  # noqa: E501
        if 'started_at__gt' in local_var_params:
            query_params.append(('started_at__gt', local_var_params['started_at__gt']))  # noqa: E501
        if 'started_at__gte' in local_var_params:
            query_params.append(('started_at__gte', local_var_params['started_at__gte']))  # noqa: E501
        if 'started_at__range' in local_var_params:
            query_params.append(('started_at__range', local_var_params['started_at__range']))  # noqa: E501
        if 'finished_at__lt' in local_var_params:
            query_params.append(('finished_at__lt', local_var_params['finished_at__lt']))  # noqa: E501
        if 'finished_at__lte' in local_var_params:
            query_params.append(('finished_at__lte', local_var_params['finished_at__lte']))  # noqa: E501
        if 'finished_at__gt' in local_var_params:
            query_params.append(('finished_at__gt', local_var_params['finished_at__gt']))  # noqa: E501
        if 'finished_at__gte' in local_var_params:
            query_params.append(('finished_at__gte', local_var_params['finished_at__gte']))  # noqa: E501
        if 'finished_at__range' in local_var_params:
            query_params.append(('finished_at__range', local_var_params['finished_at__range']))  # noqa: E501
        if 'parent' in local_var_params:
            query_params.append(('parent', local_var_params['parent']))  # noqa: E501
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))  # noqa: E501
        if 'started_at' in local_var_params:
            query_params.append(('started_at', local_var_params['started_at']))  # noqa: E501
        if 'finished_at' in local_var_params:
            query_params.append(('finished_at', local_var_params['finished_at']))  # noqa: E501
        if 'page' in local_var_params:
            query_params.append(('page', local_var_params['page']))  # noqa: E501
        if 'page_size' in local_var_params:
            query_params.append(('page_size', local_var_params['page_size']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '/pulp/api/v3/tasks/', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='InlineResponse2003',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tasks_read(self, task_href, **kwargs):  # noqa: E501
        """Inspect a task  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_read(task_href, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str task_href: URI of Task. e.g.: /pulp/api/v3/tasks/1/ (required)
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: Task
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        return self.tasks_read_with_http_info(task_href, **kwargs)  # noqa: E501

    def tasks_read_with_http_info(self, task_href, **kwargs):  # noqa: E501
        """Inspect a task  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tasks_read_with_http_info(task_href, async_req=True)
        >>> result = thread.get()

        :param async_req bool: execute request asynchronously
        :param str task_href: URI of Task. e.g.: /pulp/api/v3/tasks/1/ (required)
        :param _return_http_data_only: response data without head status code
                                       and headers
        :param _preload_content: if False, the urllib3.HTTPResponse object will
                                 be returned without reading/decoding response
                                 data. Default is True.
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :return: tuple(Task, status_code(int), headers(HTTPHeaderDict))
                 If the method is called asynchronously,
                 returns the request thread.
        """

        local_var_params = locals()

        all_params = ['task_href']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tasks_read" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'task_href' is set
        if ('task_href' not in local_var_params or
                local_var_params['task_href'] is None):
            raise ApiValueError("Missing the required parameter `task_href` when calling `tasks_read`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'task_href' in local_var_params:
            path_params['task_href'] = local_var_params['task_href']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['Basic']  # noqa: E501

        return self.api_client.call_api(
            '{task_href}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Task',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)
