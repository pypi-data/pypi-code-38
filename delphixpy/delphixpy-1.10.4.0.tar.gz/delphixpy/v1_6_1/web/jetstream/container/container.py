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
Package "jetstream.container"
"""
API_VERSION = "1.6.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_6_1 import response_validator

def create(engine, js_data_container_create_parameters):
    """
    Create a new JSDataContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param js_data_container_create_parameters: Payload object.
    :type js_data_container_create_parameters:
        :py:class:`v1_6_1.web.vo.JSDataContainerCreateParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container"
    response = engine.post(url, js_data_container_create_parameters.to_dict(dirty=True) if js_data_container_create_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified JSDataContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    :rtype: :py:class:`v1_6_1.web.vo.JSDataContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSDataContainer'], returns_list=False, raw_result=raw_result)

def get_all(engine, owner=None, template=None):
    """
    List the data containers defined in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param owner: Restrict data containers to those belonging to the specified
        user. This option is mutually exclusive with the "template" option.
    :type owner: ``TEXT_TYPE``
    :param template: Restrict data containers to those provisioned from the
        specified template. This option is mutually exclusive with the "owner"
        option.
    :type template: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_6_1.web.vo.JSDataContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container"
    query_params = {"owner": owner, "template": template}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSDataContainer'], returns_list=True, raw_result=raw_result)

def update(engine, ref, js_data_container=None):
    """
    Update the specified JSDataContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    :param js_data_container: Payload object.
    :type js_data_container: :py:class:`v1_6_1.web.vo.JSDataContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s" % ref
    response = engine.post(url, js_data_container.to_dict(dirty=True) if js_data_container else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref, js_data_container_delete_parameters=None):
    """
    Delete this data container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    :param js_data_container_delete_parameters: Payload object.
    :type js_data_container_delete_parameters:
        :py:class:`v1_6_1.web.vo.JSDataContainerDeleteParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/delete" % ref
    response = engine.post(url, js_data_container_delete_parameters.to_dict(dirty=True) if js_data_container_delete_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def reset(engine, ref):
    """
    Reset the data container to the last data operation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/reset" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def restore(engine, ref, js_timeline_point_parameters):
    """
    Restore this data container to the point specified by the Jet Stream
    timeline point parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    :param js_timeline_point_parameters: Payload object.
    :type js_timeline_point_parameters:
        :py:class:`v1_6_1.web.vo.JSTimelinePointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/restore" % ref
    response = engine.post(url, js_timeline_point_parameters.to_dict(dirty=True) if js_timeline_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable(engine, ref):
    """
    Enable this data container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/enable" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def refresh(engine, ref):
    """
    Refresh this data container to the latest data from its template.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/refresh" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def disable(engine, ref):
    """
    Disable this data container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/disable" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def recover(engine, ref):
    """
    Recover this data container from the INCONSISTENT state.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/recover" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def get_active_branch_at_time(engine, ref, js_data_container_active_branch_parameters):
    """
    Return the branch that was active for the given time.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_1.web.objects.JSDataContainer.JSDataContainer
        ` object
    :type ref: ``str``
    :param js_data_container_active_branch_parameters: Payload object.
    :type js_data_container_active_branch_parameters:
        :py:class:`v1_6_1.web.vo.JSDataContainerActiveBranchParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/%s/getActiveBranchAtTime" % ref
    response = engine.post(url, js_data_container_active_branch_parameters.to_dict(dirty=True) if js_data_container_active_branch_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def list_by_top_operation_count(engine, template=None, max_result_size=None):
    """
    Return child data containers for a given template sorted by operationCount.
    Can optionally limit to the top maxResultSize data containers.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_1.delphix_engine.DelphixEngine`
    :param template: The given data template.
    :type template: ``TEXT_TYPE``
    :param max_result_size: The maximum number of results to return. A value of
        0 means all are returned.
    :type max_result_size: ``int``
    :rtype: ``list`` of :py:class:`v1_6_1.web.vo.JSDataContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/container/listByTopOperationCount"
    query_params = {"template": template, "maxResultSize": max_result_size}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSDataContainer'], returns_list=True, raw_result=raw_result)

