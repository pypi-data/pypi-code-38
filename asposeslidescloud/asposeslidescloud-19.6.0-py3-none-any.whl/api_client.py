# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------
from __future__ import absolute_import

import os
import re
import json
import logging
import mimetypes
import sys
import tempfile
import traceback
from multiprocessing.pool import ThreadPool

from datetime import date, datetime

# python 2 and python 3 compatibility library
from six import PY3, integer_types, iteritems, text_type
from six.moves.urllib.parse import quote

from asposeslidescloud import models
from asposeslidescloud.configuration import Configuration
from asposeslidescloud import oauth_response
from asposeslidescloud import error_message
from asposeslidescloud.rest import ApiException, RESTClientObject

class ApiClient(object):

    PRIMITIVE_TYPES = (float, bool, bytes, text_type) + integer_types
    NATIVE_TYPES_MAPPING = {
        'int': int,
        'long': int if PY3 else long,
        'float': float,
        'str': str,
        'bool': bool,
        'date': date,
        'datetime': datetime,
        'object': object,
        "ErrorMessage": getattr(error_message, "ErrorMessage")
    }

    def __init__(self, configuration=None, header_name=None, header_value=None, cookie=None):
        if configuration is None:
            configuration = Configuration()
        self.configuration = configuration

        self.pool = ThreadPool()
        self.rest_client = RESTClientObject(configuration)
        self.default_headers = {'x-aspose-client': 'python sdk', 'x-aspose-version': '19.6.0'}
        if configuration.timeout:
            self.default_headers['x-aspose-timeout'] = configuration.timeout
       
        if header_name is not None:
            self.default_headers[header_name] = header_value
        self.cookie = cookie
    
    def __del__(self):
        self.pool.close()
        self.pool.join()

    def set_default_header(self, header_name, header_value):
        self.default_headers[header_name] = header_value

    def __call_api(self, resource_path, method,
                   path_params=None, query_params=None, header_params=None,
                   body=None, post_params=None, files=None,
                   response_type=None, auth_settings=None,
                   _return_http_data_only=None, collection_formats=None, _preload_content=True,
                   _request_timeout=None):
        config = self.configuration

        # header parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if self.cookie:
            header_params['Cookie'] = self.cookie
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)
            header_params = dict(self.parameters_to_tuples(header_params,
                                                           collection_formats))

        # path parameters
        if path_params:
            path_params = self.sanitize_for_serialization(path_params)
            path_params = self.parameters_to_tuples(path_params,
                                                    collection_formats)
            for k, v in path_params:
                if not v:
                    resource_path = resource_path.replace('/{%s}' % k, '')
                else:
                    # specified safe chars, encode everything
                    resource_path = resource_path.replace('{%s}' % k, quote(str(v), safe=config.safe_chars_for_path_param))

        # query parameters
        if query_params:
            query_params = self.sanitize_for_serialization(query_params)
            query_params = self.parameters_to_tuples(query_params, collection_formats)

        # post parameters
        if post_params or files:
            post_params = self.sanitize_for_serialization(post_params)
            post_params = self.parameters_to_tuples(post_params, collection_formats)

        self.__authenticate(header_params, _request_timeout)

        # body
        if body:
            body = self.sanitize_for_serialization(body)

        # request url
        url = self.configuration.host + resource_path

        # perform request and return response
        response_data = self.__call_api_with_refresh(
            method, url, query_params, header_params, post_params, body, files, _preload_content, _request_timeout)

        self.last_response = response_data

        return_data = response_data
        if _preload_content:
            # deserialize response data
            if response_type:
                return_data = self.deserialize(response_data, response_type)
            else:
                return_data = None

        if _return_http_data_only:
            return (return_data)
        else:
            return (return_data, response_data.status, response_data.getheaders())

    def __call_api_with_refresh(self, method, url, query_params, header_params, post_params, body, files, _preload_content, _request_timeout):
        try:
            try:
                return self.request(method, url,
                                     query_params=query_params,
                                     headers=header_params,
                                     post_params=post_params, body = body, files = files,
                                     _preload_content=_preload_content,
                                     _request_timeout=_request_timeout)
            except ApiException as ex:
                if ex.status == 401:
                    self.configuration.access_token = None
                    self.__authenticate(header_params, _request_timeout)
                    return self.request(method, url,
                                     query_params=query_params,
                                     headers=header_params,
                                     post_params=post_params, body = body, files = files,
                                     _preload_content=_preload_content,
                                     _request_timeout=_request_timeout)
                raise ex
        except ApiException as ex:
            if ex.body:
                message = self.deserialize_model(json.loads(ex.body), "ErrorMessage")
                self.__set_exception_message(ex, message)
            raise ex

    def __set_exception_message(self, ex, message):
        if message:
            if message.error:
                self.__set_exception_message(ex, message.error)
            elif message.message:
                ex.body = message.message

    def __authenticate(self, header_params, _request_timeout):
        if not self.configuration.access_token:
            post_params = {
                'grant_type': 'client_credentials',
                'client_id': self.configuration.app_sid,
                'client_secret': self.configuration.app_key
            }
            config = self.configuration
            token_response = self.request(
                'POST', config.auth_base_url + "/connect/token", post_params=post_params, _request_timeout=_request_timeout)
            token_data = json.loads(token_response.data)
            token_klass = getattr(oauth_response, "OAuthResponse")
            token = self.__deserialize_model(token_data, token_klass)
            config.access_token = token.access_token
        header_params["Authorization"] = "Bearer " + self.configuration.access_token

    def sanitize_for_serialization(self, obj):
        """
        Builds a JSON POST object.

        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is swagger model, return the properties dict.

        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        if isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        if isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj)
                    for sub_obj in obj]
        if isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj)
                         for sub_obj in obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            # Convert model obj to dict except
            # attributes `swagger_types`, `attribute_map`
            # and attributes which value is not None.
            # Convert attribute name to json key in
            # model definition for request.
            obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                        for attr, _ in iteritems(obj.swagger_types)
                        if getattr(obj, attr) is not None}

        return {key: self.sanitize_for_serialization(val)
                for key, val in iteritems(obj_dict)}

    def deserialize(self, response, response_type):
        """
        Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: class literal for
            deserialized object, or string of class name.

        :return: deserialized object.
        """
        # handle file downloading
        # save response body into a tmp file and return the instance
        if response_type == "file":
            return self.__deserialize_file(response)

        # fetch data from response object
        try:
            data = json.loads(response.data)
        except ValueError:
            data = response.data

        return self.deserialize_model(data, response_type)

    def deserialize_model(self, data, klass):
        """
        Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if type(klass) == str:
            if klass.startswith('list['):
                sub_kls = re.match('list\[(.*)\]', klass).group(1)
                return [self.deserialize_model(sub_data, sub_kls)
                        for sub_data in data]

            if klass.startswith('dict('):
                sub_kls = re.match('dict\(([^,]*), (.*)\)', klass).group(2)
                return {k: self.deserialize_model(v, sub_kls)
                        for k, v in iteritems(data)}

            # convert str to class
            if klass in self.NATIVE_TYPES_MAPPING:
                klass = self.NATIVE_TYPES_MAPPING[klass]
            else:
                klass = getattr(models, klass)

        if klass in self.PRIMITIVE_TYPES:
            return self.__deserialize_primitive(data, klass)
        elif klass == object:
            return self.__deserialize_object(data)
        elif klass == date:
            return self.__deserialize_date(data)
        elif klass == datetime:
            return self.__deserialize_datatime(data)
        else:
            return self.__deserialize_model(data, klass)

    def call_api(self, resource_path, method,
                 path_params=None, query_params=None, header_params=None,
                 body=None, post_params=None, files=None,
                 response_type=None, auth_settings=None, is_async=None,
                 _return_http_data_only=None, collection_formats=None, _preload_content=True,
                 _request_timeout=None):
        """
        Makes the HTTP request (synchronous) and return the deserialized data.
        To make an async request, define a function for callback.

        :param resource_path: Path to method endpoint.
        :param method: Method to call.
        :param path_params: Path parameters in the url.
        :param query_params: Query parameters in the url.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params dict: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param auth_settings list: Auth Settings names for the request.
        :param response: Response data type.
        :param files dict: key -> filename, value -> filepath,
            for `multipart/form-data`.
        :param is_async bool: execute request asynchronously
        :param _return_http_data_only: response data without head status code and headers
        :param collection_formats: dict of collection formats for path, query,
            header, and post parameters.
        :param _preload_content: if False, the urllib3.HTTPResponse object will be returned without
                                 reading/decoding response data. Default is True.
        :param _request_timeout: timeout setting for this request. If one number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of (connection, read) timeouts.
        :return:
            If provide parameter callback,
            the request will be called asynchronously.
            The method will return the request thread.
            If parameter callback is None,
            then the method will return the response directly.
        """
        if not is_async:
            return self.__call_api(resource_path, method,
                                   path_params, query_params, header_params,
                                   body, post_params, files,
                                   response_type, auth_settings,
                                   _return_http_data_only, collection_formats, _preload_content, _request_timeout)
        else:
            thread = self.pool.apply_async(self.__call_api, (resource_path, method,
                                           path_params, query_params,
                                           header_params, body,
                                           post_params, files,
                                           response_type, auth_settings,
                                           _return_http_data_only,
                                           collection_formats, _preload_content, _request_timeout))
        return thread

    def request(self, method, url, query_params=None, headers=None,
                post_params=None, body=None, files=None, _preload_content=True, _request_timeout=None):
        """
        Makes the HTTP request using RESTClient.
        """
        if method == "GET":
            return self.rest_client.GET(url,
                                        query_params=query_params,
                                        _preload_content=_preload_content,
                                        _request_timeout=_request_timeout,
                                        headers=headers)
        elif method == "HEAD":
            return self.rest_client.HEAD(url,
                                         query_params=query_params,
                                         _preload_content=_preload_content,
                                         _request_timeout=_request_timeout,
                                         headers=headers)
        elif method == "OPTIONS":
            return self.rest_client.OPTIONS(url,
                                            query_params=query_params,
                                            headers=headers,
                                            post_params=post_params,
                                            files=files,
                                            _preload_content=_preload_content,
                                            _request_timeout=_request_timeout,
                                            body=body)
        elif method == "POST":
            return self.rest_client.POST(url,
                                         query_params=query_params,
                                         headers=headers,
                                         post_params=post_params,
                                         files=files,
                                         _preload_content=_preload_content,
                                         _request_timeout=_request_timeout,
                                         body=body)
        elif method == "PUT":
            return self.rest_client.PUT(url,
                                        query_params=query_params,
                                        headers=headers,
                                        post_params=post_params,
                                        files=files,
                                        _preload_content=_preload_content,
                                        _request_timeout=_request_timeout,
                                        body=body)
        elif method == "PATCH":
            return self.rest_client.PATCH(url,
                                          query_params=query_params,
                                          headers=headers,
                                          post_params=post_params,
                                          files=files,
                                          _preload_content=_preload_content,
                                          _request_timeout=_request_timeout,
                                          body=body)
        elif method == "DELETE":
            return self.rest_client.DELETE(url,
                                           query_params=query_params,
                                           headers=headers,
                                           _preload_content=_preload_content,
                                           _request_timeout=_request_timeout,
                                           body=body)
        else:
            raise ValueError(
                "http method must be `GET`, `HEAD`, `OPTIONS`,"
                " `POST`, `PATCH`, `PUT` or `DELETE`."
            )

    def parameters_to_tuples(self, params, collection_formats):
        """
        Get parameters as list of tuples, formatting collections.

        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: Parameters as list of tuples, collections formatted
        """
        new_params = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in iteritems(params) if isinstance(params, dict) else params:
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == 'multi':
                    new_params.extend((k, value) for value in v)
                else:
                    if collection_format == 'ssv':
                        delimiter = ' '
                    elif collection_format == 'tsv':
                        delimiter = '\t'
                    elif collection_format == 'pipes':
                        delimiter = '|'
                    else:  # csv is the default
                        delimiter = ','
                    new_params.append(
                        (k, delimiter.join(str(value) for value in v)))
            else:
                new_params.append((k, v))
        return new_params

    def select_header_accept(self, accepts):
        """
        Returns `Accept` based on an array of accepts provided.

        :param accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]

        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    def select_header_content_type(self, content_types):
        """
        Returns `Content-Type` based on an array of content_types provided.

        :param content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return 'application/json'

        content_types = [x.lower() for x in content_types]

        if 'application/json' in content_types or '*/*' in content_types:
            return 'application/json'
        else:
            return content_types[0]

    def update_params_for_auth(self, headers, querys, auth_settings):
        """
        Updates header and query params based on authentication setting.

        :param headers: Header parameters dict to be updated.
        :param querys: Query parameters tuple list to be updated.
        :param auth_settings: Authentication setting identifiers list.
        """
        if not auth_settings:
            return

        for auth in auth_settings:
            auth_setting = self.configuration.auth_settings().get(auth)
            if auth_setting:
                if not auth_setting['value']:
                    continue
                elif auth_setting['in'] == 'header':
                    headers[auth_setting['key']] = auth_setting['value']
                elif auth_setting['in'] == 'query':
                    querys.append((auth_setting['key'], auth_setting['value']))
                else:
                    raise ValueError(
                        'Authentication token must be in `query` or `header`'
                    )

    def __deserialize_file(self, response):
        """
        Saves response body into a file in a temporary folder,
        using the filename from the `Content-Disposition` header if provided.

        :param response:  RESTResponse.
        :return: file path.
        """
        fd, path = tempfile.mkstemp(dir=self.configuration.temp_folder_path)
        os.close(fd)
        os.remove(path)

        content_disposition = response.getheader("Content-Disposition")
        if content_disposition:
            filename = re.search(r'filename=[\'"]?([^\'"\s]+)[\'"]?', content_disposition).group(1)
            path = self.__get_file_name(os.path.dirname(path), filename)
        mode = 'w'
        if (isinstance(response.data, bytes)):
            mode = 'wb'
        with open(path, mode) as f:
            f.write(response.data)

        return path

    def __get_file_name(self, dirname, filename):
        """
        Gets a file path for a directory name and a file name and generates an alternative name if a file with such a name already exists.

        :param dirname:  directory name.
        :param filename:  file name.
        :return: file path.
        """
        filenames = os.path.splitext(filename)
        index = 0
        postfix = ""
        while True:
            path = os.path.join(dirname, filenames[0] + postfix + filenames[1])
            if not os.path.exists(path):
                return path
            index += 1
            postfix = "_" + str(index)

    def __deserialize_primitive(self, data, klass):
        """
        Deserializes string to primitive type.

        :param data: str.
        :param klass: class literal.

        :return: int, long, float, str, bool.
        """
        try:
            return klass(data)
        except UnicodeEncodeError:
            return unicode(data)
        except TypeError:
            return data

    def __deserialize_object(self, value):
        """
        Return a original value.

        :return: object.
        """
        return value

    def __deserialize_date(self, string):
        """
        Deserializes string to date.

        :param string: str.
        :return: date.
        """
        try:
            from dateutil.parser import parse
            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise ApiException(
                status=0,
                reason="Failed to parse `{0}` into a date object".format(string)
            )

    def __deserialize_datatime(self, string):
        """
        Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.
        :return: datetime.
        """
        try:
            from dateutil.parser import parse
            return parse(string)
        except ImportError:
            return string
        except ValueError:
            raise ApiException(
                status=0,
                reason=(
                    "Failed to parse `{0}` into a datetime object"
                    .format(string)
                )
            )

    def __deserialize_model(self, data, klass):
        """
        Deserializes list or dict to model.

        :param data: dict, list.
        :param klass: class literal.
        :return: model object.
        """
        if not klass.swagger_types:
            return data

        kwargs = {}
        self.__fill_model_args(kwargs, data, klass)
        return klass(**kwargs)

    def __fill_model_args(self, args, data, klass):
        """
        Fills list of attribures for class.

        :param args: attribute list.
        :param data: dict, list.
        :param klass: class literal.
        """
        if klass.swagger_types is not None:
            for attr, attr_type in iteritems(klass.swagger_types):
                if data is not None and klass.attribute_map[attr] in data and isinstance(data, (list, dict)):
                    value = data[klass.attribute_map[attr]]
                    args[attr] = self.deserialize_model(value, attr_type)
            base_klass = klass.__bases__[0]
            if not base_klass == object:
                self.__fill_model_args(args, data, base_klass)
