# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Access base class to handle _restclient calls"""
import copy
import os
import logging
import time
import json

from json import JSONEncoder
from abc import ABCMeta, abstractmethod
from six import raise_from, add_metaclass, PY2

from .constants import (ATTRIBUTE_CONTINUATION_TOKEN_NAME, ATTRIBUTE_VALUE_NAME, QUERY_PARAMS_KEY)
from azureml._async import AsyncTask, WorkerPool
from azureml._logging import ChainedIdentity
from azureml.exceptions import UserErrorException
from msrest.serialization import Model
from msrest.exceptions import HttpOperationError
from requests.packages.urllib3.exceptions import SSLError, ProtocolError

# http exceptions have backwards compatability issues across python 2 and python 3
#  Base exception for RemoteDisconnected https://stackoverflow.com/questions/43676939
if PY2:
    from httplib import HTTPException
    HTTP_EXCEPTIONS = (HTTPException, ProtocolError)
else:
    from http.client import HTTPException
    HTTP_EXCEPTIONS = (ConnectionError, HTTPException, ProtocolError)

NUMBER_TO_DOWNLOAD = 'total_count'
ASYNC_KEY = 'is_async'
PAGINATED_KEY = 'is_paginated'
NEW_IDENT = 'new_ident'

DEFAULT_BACKOFF_ENV_VAR = "AZUREML_DEFAULT_BACKOFF"
DEFAULT_RETRIES_ENV_VAR = "AZUREML_DEFAULT_RETRIES"

DEFAULT_BACKOFF = int(os.environ.get(DEFAULT_BACKOFF_ENV_VAR, "32"))
DEFAULT_RETRIES = int(os.environ.get(DEFAULT_RETRIES_ENV_VAR, "3"))
module_logger = logging.getLogger(__name__)


class _ErrorEncoder(JSONEncoder):
    def default(self, obj):
        return getattr(obj, "__dict__", {})


@add_metaclass(ABCMeta)
class ClientBase(ChainedIdentity):
    """
    Client Base class

    :param host: The base path for the server to call.
    :type host: str
    :param auth: Client authentication
    :type auth: azureml.core.authentication.AbstractAuthentication
    """
    _worker_pool = None

    def __init__(self, worker_pool=None, logger=None, user_agent=None, **kwargs):
        """
        Constructor of the class.
        """

        # TODO: Resolve _restclient's dependency on core so this block can be moved
        from azureml._restclient.models import (DebugInfoResponse, InnerErrorResponse, ErrorDetails, RootError,
                                                ErrorResponse)

        def pretty_print(self):
            return json.dumps(self, indent=4, cls=_ErrorEncoder)

        classes_to_pretty_print = [DebugInfoResponse, InnerErrorResponse, ErrorDetails, RootError, ErrorResponse]
        for class_to_pretty_print in classes_to_pretty_print:
            class_to_pretty_print.__str__ = class_to_pretty_print.__repr__ = pretty_print
        # end TODO block

        super(ClientBase, self).__init__(**kwargs)
        if logger is not None:
            self._logger.warning("Deprecated kwarg logger, renamed to _parent_logger. "
                                 "logger kwarg was ignored.")

        self._client = self.get_rest_client(user_agent=user_agent)
        # Enable logging for all requests and responses if log level is logging.DEBUG
        # logs request body and response body, does not log authentication tokens
        self._client.config.enable_http_logger = True
        # We override a config in the retry policy to throw exceptions after retry.
        # By default this is True. We set it to false to get the full error trace, including url and
        # status code of the last retry. Otherwise, the error message is 'too many 500 error responses',
        # which is not useful.
        self._client.config.retry_policy.policy.raise_on_status = False

        self._pool = worker_pool if worker_pool is not None else ClientBase._get_worker_pool()

    @property
    def retries(self):
        """Total number of allowed retries."""
        return self._client.config.retry_policy.retries

    @retries.setter
    def retries(self, value):
        self._client.config.retry_policy.retries = value

    @property
    def backoff_factor(self):
        """
        Factor by which back-off delay is incrementally increased.
        back-off delay = {backoff factor} * (2 ^ ({number of total retries} - 1))
        """
        return self._client.config.retry_policy.backoff_factor

    @backoff_factor.setter
    def backoff_factor(self, value):
        self._client.config.retry_policy.backoff_factor = value

    @property
    def max_backoff(self):
        """Max retry back-off delay."""
        return self._client.config.retry_policy.max_backoff

    @max_backoff.setter
    def max_backoff(self, value):
        self._client.config.retry_policy.max_backoff = value

    @abstractmethod
    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        raise NotImplementedError

    @classmethod
    def _get_worker_pool(cls):
        if cls._worker_pool is None:
            cls._worker_pool = WorkerPool(_parent_logger=module_logger)
            module_logger.info("Created a worker pool for first use")
        return cls._worker_pool

    @property
    def _host(self):
        return self._client.config.base_url

    @property
    def auth(self):
        return self._client.config.credentials

    def _call_api(self, func, *args, **kwargs):
        """make a function call with arguments
        This method makes a synchronous call by default. To make an
        asynchronous call, please pass is_async=True
        >>> task = self.call_api(func, *args, **kwargs, is_async=True)
        >>> result = task.wait()

        :param func function object: function to execute
        :param is_async bool: execute request asynchronously
        :param args list: list of arguments
        :param kwargs dict: arguments as dictionary
        :return:
            If is_async parameter is True,
            the request is called asynchronously.
            The method returns azureml._async.AsyncTask object
            If parameter is_async is False or missing,
            the method returns the response directly.
        """
        if not callable(func):
            raise TypeError('Argument is not callable')

        is_async = kwargs.pop(ASYNC_KEY, False)
        with self._log_context("{}-async:{}".format(func.__name__, is_async)):
            if is_async:
                future = self._pool.submit(self._execute_with_base_arguments, func, *args, **kwargs)
                new_ident = kwargs.pop(NEW_IDENT, None)
                ident = new_ident if new_ident is not None else func.__name__
                return AsyncTask(future, _ident=ident, _parent_logger=self._logger)
            else:
                return self._execute_with_base_arguments(func, *args, **kwargs)

    def _call_paginated_api(self, func, *args, **kwargs):
        """make a paginated api call with arguments
        :param func function object: function to execute
        :param total_count int: the most number of items to return
        :param args list: list of arguments
        :param kwargs dict: arguments as dictionary
        :return:
            a generator of dto_items
        """
        if not callable(func):
            raise TypeError('Argument is not callable')

        total = kwargs.pop(NUMBER_TO_DOWNLOAD, 0)
        kwargs[ASYNC_KEY] = True
        count = 0
        next_page = self._call_api(func, *args, **kwargs)
        while(True):
            paginated_dto = next_page.wait(awaiter_name="ApiPagination")
            if not paginated_dto:
                break

            token = ClientBase._get_attribute(paginated_dto, ATTRIBUTE_CONTINUATION_TOKEN_NAME)
            if token:
                existing_token = kwargs.get(ATTRIBUTE_CONTINUATION_TOKEN_NAME, None)
                if existing_token == token:
                    token = None
                else:
                    if QUERY_PARAMS_KEY in kwargs:
                        setattr(kwargs[QUERY_PARAMS_KEY], ATTRIBUTE_CONTINUATION_TOKEN_NAME, token)
                    else:
                        kwargs[ATTRIBUTE_CONTINUATION_TOKEN_NAME] = token
                    next_page = self._call_api(func, *args, **kwargs)

            value_as_list = ClientBase._get_attribute(paginated_dto, ATTRIBUTE_VALUE_NAME)
            if not value_as_list:
                break

            for dto in value_as_list:
                if getattr(dto, "hidden", False) is not True:
                    yield dto
                count += 1
                if count == total:
                    return

            if not token:
                break

    def _execute_with_base_arguments(self, func, *args, **kwargs):
        back_off = self.backoff_factor
        total_retry = 0 if self.retries < 0 else self.retries
        ssl_error_handler = self._handle_SSLError
        return ClientBase._execute_func_internal(
            back_off, total_retry, ssl_error_handler, self._logger, func, *args, **kwargs)

    @classmethod
    def _execute_func_internal(cls, back_off, total_retry, ssl_error_handler, logger, func, *args, **kwargs):
        if not callable(func):
            raise TypeError('Argument is not callable')

        left_retry = total_retry
        while left_retry >= 0:
            try:
                return func(*args, **kwargs)
            except SSLError as e:
                if left_retry == 0:
                    raise e

                ssl_error_handler(e.msg)
                cls._wait_for_retry(back_off, left_retry, total_retry)
                left_retry -= 1
            except HTTP_EXCEPTIONS:
                cls._wait_for_retry(back_off, left_retry, total_retry)
                left_retry -= 1
            except HttpOperationError as err:
                if err.response.status_code == 403:
                    error_meg = """
Operation returned an invalid status code 'Forbidden'. The possible reason could be:
1. You are not authorized to access this resource, or directory listing denied.
2. you may not login your azure service, or use other subscription, you can check your
   default account by running azure cli commend:
   'az account list -o table'.
3. You have multiple objects/login session opened, please close all session and try again.
                    """
                    raise_from(UserErrorException(error_meg), err)

                elif err.response.status_code == 429:
                    if left_retry == 0:
                        raise
                    logger.debug("There were too many requests. Try again soon.")
                    back_off = DEFAULT_BACKOFF
                    cls._wait_for_retry(back_off, left_retry, total_retry)
                    left_retry -= 1
                else:
                    raise

    @classmethod
    def _execute_func(cls, func, *args, **kwargs):
        def nop(*args, **kwargs):
            pass

        return cls._execute_func_internal(
            DEFAULT_BACKOFF, DEFAULT_RETRIES, nop, logging.getLogger(__name__), func, *args, **kwargs)

    @staticmethod
    def _wait_for_retry(back_off, left_retry, total_retry):
        delay = back_off * 2 ** (total_retry - left_retry - 1)
        time.sleep(delay)

    def _handle_SSLError(self, error_msg):
        self._logger.debug('Sending requests failed, {}'.format(error_msg))
        history = getattr(self._client.config.retry_policy.policy, 'history')
        if history is not None:
            self._logger.debug("Retry history:{}".format(history))
        self._logger.debug('Retry to send request again')

    def _combine_paginated_base(self, exec_func, func, count_to_download=0, *args, **kwargs):
        if not callable(exec_func):
            raise TypeError('Argument is not callable')

        paginated_dto = exec_func(func,
                                  *args,
                                  **kwargs)

        not_exists = 'Not_Exists'
        is_return_as_dict = kwargs.get('return_as_dict', True)
        token = getattr(
            paginated_dto, ATTRIBUTE_CONTINUATION_TOKEN_NAME, not_exists)
        if token == not_exists:
            raise TypeError("property '{0}' is expected in return of function '{1}'."
                            .format(ATTRIBUTE_CONTINUATION_TOKEN_NAME, func.__name__))

        value = getattr(paginated_dto, ATTRIBUTE_VALUE_NAME, not_exists)
        if value == not_exists:
            raise TypeError("property '{0}' is expected in return of function '{1}'."
                            .format(ATTRIBUTE_VALUE_NAME, func.__name__))

        is_get_all_data = count_to_download < 1
        data = []
        if is_return_as_dict:
            data.extend(v.__dict__ for v in value)
        else:
            data.extend(value)
        total_item_got = len(data)
        more_to_come = is_get_all_data if is_get_all_data else count_to_download > total_item_got

        if not kwargs:
            kwargs_copy = dict()
        else:
            kwargs_copy = copy.deepcopy(kwargs)

        data_list = []
        while token and more_to_come is True:
            kwargs_copy[ATTRIBUTE_CONTINUATION_TOKEN_NAME] = token
            paginated_dto = exec_func(func,
                                      *args,
                                      **kwargs_copy)
            if is_return_as_dict:
                data_list.extend(v.__dict__ for v in getattr(
                    paginated_dto, ATTRIBUTE_VALUE_NAME))
            else:
                data_list.extend(getattr(paginated_dto, ATTRIBUTE_VALUE_NAME))

            data.extend(data_list)
            token = getattr(paginated_dto, ATTRIBUTE_CONTINUATION_TOKEN_NAME)
            total_item_got += len(data_list)
            more_to_come = is_get_all_data if is_get_all_data else count_to_download > total_item_got
            del data_list[:]

        if is_get_all_data is False and total_item_got > count_to_download:
            del data[count_to_download:total_item_got]
        return data

    @staticmethod
    def dto_to_dictionary(dto, keep_readonly=True, key_transformer=None):
        """Return a dict that can be JSONify using json.dump.
        :param ~_restclient.models dto: object to transform
        :param bool keep_readonly: If you want to serialize the readonly attributes
        :param function key_transformer: A key transformer function.
                                         Example: attribute_transformer() in msrest.serialization.
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        if dto is None:
            return None

        if not isinstance(dto, Model):
            raise TypeError("Argument is not a Model type")

        if key_transformer is not None:
            return dto.as_dict(keep_readonly=keep_readonly, key_transformer=key_transformer)

        return dto.as_dict(keep_readonly=keep_readonly)

    @staticmethod
    def _get_attribute(value, attr_name):
        try:
            return getattr(value, attr_name)
        except AttributeError:
            raise AttributeError("property '{0}' is expected in object type '{1}'."
                                 .format(attr_name, type(value)))
