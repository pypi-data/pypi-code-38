#
# Copyright 2019 by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Package "jetstream.operation"
"""
API_VERSION = "1.4.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_4_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified JSOperation object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.JSOperation.JSOperation` object
    :type ref: ``str``
    :rtype: :py:class:`v1_4_0.web.vo.JSOperation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/operation/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSOperation'], returns_list=False, raw_result=raw_result)

def get_all(engine, data_layout=None, after_count=None, data_time=None, before_count=None, data_start_time=None, branch=None, data_end_time=None):
    """
    Lists the Jet Stream action history for a data layout.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param data_layout: Limit operations to the specific data layout. This
        option is mutually exclusive with the "branch" option.
    :type data_layout: ``TEXT_TYPE``
    :param after_count: The suggested maximum number of visible operations
        after "dataTime" that should be returned. If there are not sufficient
        events after additional events before may be returned.
    :type after_count: ``int``
    :param data_time: Limit operations that occured around the specified
        "dataTime". "beforeCount" and "afterCount" should specify the number of
        events to be returned.
    :type data_time: ``TEXT_TYPE``
    :param before_count: The suggested maximum number of visible operations
        prior to "dataTime" that should be returned. If there are not
        sufficient events before additional events after may be returned.
    :type before_count: ``int``
    :param data_start_time: Operations with "dataTime" after this value will be
        returned. Used with "dataEndTime" to return a set of operations between
        two dates.
    :type data_start_time: ``TEXT_TYPE``
    :param branch: Limit operations to the specified branch. This option is
        mutually exclusive with the "dataLayout" option.
    :type branch: ``TEXT_TYPE``
    :param data_end_time: Operations with "dataTime" before this value will be
        returned. Used with "dataStartTime" to return a set of operations
        between two dates.
    :type data_end_time: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_4_0.web.vo.JSOperation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/operation"
    query_params = {"dataLayout": data_layout, "afterCount": after_count, "dataTime": data_time, "beforeCount": before_count, "dataStartTime": data_start_time, "branch": branch, "dataEndTime": data_end_time}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSOperation'], returns_list=True, raw_result=raw_result)

def list_operations_by_action(engine, action=None):
    """
    Return the list of operations spawned by the root action of the given
    action.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param action: The given action.
    :type action: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_4_0.web.vo.JSOperation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/operation/listOperationsByAction"
    query_params = {"action": action}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSOperation'], returns_list=True, raw_result=raw_result)

def endpoint(engine, js_operation_endpoint_parameters):
    """
    Return the first and last operation for the specified parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param js_operation_endpoint_parameters: Payload object.
    :type js_operation_endpoint_parameters:
        :py:class:`v1_4_0.web.vo.JSOperationEndpointParameters`
    :rtype: :py:class:`v1_4_0.web.vo.JSOperationEndpoint`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/operation/endpoint"
    response = engine.post(url, js_operation_endpoint_parameters.to_dict(dirty=True) if js_operation_endpoint_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSOperationEndpoint'], returns_list=False, raw_result=raw_result)

def list_operations_by_job(engine, job=None):
    """
    Return the list of operations spawned by the root action of the given job.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param job: The given job.
    :type job: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_4_0.web.vo.JSOperation`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/operation/listOperationsByJob"
    query_params = {"job": job}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSOperation'], returns_list=True, raw_result=raw_result)

