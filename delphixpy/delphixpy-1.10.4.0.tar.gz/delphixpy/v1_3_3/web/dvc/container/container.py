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
Package "dvc.container"
"""
API_VERSION = "1.3.3"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_3_3 import response_validator

def create(engine, dvc_application_container_create_parameters):
    """
    Create a new DVCApplicationContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param dvc_application_container_create_parameters: Payload object.
    :type dvc_application_container_create_parameters:
        :py:class:`v1_3_3.web.vo.DVCApplicationContainerCreateParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container"
    response = engine.post(url, dvc_application_container_create_parameters.to_dict(dirty=True) if dvc_application_container_create_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified DVCApplicationContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    :rtype: :py:class:`v1_3_3.web.vo.DVCApplicationContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCApplicationContainer'], returns_list=False, raw_result=raw_result)

def get_all(engine, owner=None, template=None):
    """
    List the application containers defined in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param owner: Restrict application containers to those belonging to the
        specified user. This option is mutually exclusive with the "template"
        option.
    :type owner: ``TEXT_TYPE``
    :param template: Restrict application containers to those provisioned from
        the specified template. This option is mutually exclusive with the
        "owner" option.
    :type template: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_3_3.web.vo.DVCApplicationContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container"
    query_params = {"owner": owner, "template": template}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCApplicationContainer'], returns_list=True, raw_result=raw_result)

def update(engine, ref, dvc_application_container=None):
    """
    Update the specified DVCApplicationContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    :param dvc_application_container: Payload object.
    :type dvc_application_container:
        :py:class:`v1_3_3.web.vo.DVCApplicationContainer`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s" % ref
    response = engine.post(url, dvc_application_container.to_dict(dirty=True) if dvc_application_container else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified DVCApplicationContainer object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def reset(engine, ref):
    """
    Reset the application container to the last data operation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s/reset" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable(engine, ref):
    """
    Enable this application container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s/enable" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def recover(engine, ref):
    """
    Recover this application container from the FAULTED state.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s/recover" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def refresh(engine, ref, dvc_timeline_point_parameters):
    """
    Refresh this application container to the point specified by the DVC
    timeline point parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    :param dvc_timeline_point_parameters: Payload object.
    :type dvc_timeline_point_parameters:
        :py:class:`v1_3_3.web.vo.DVCTimelinePointParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s/refresh" % ref
    response = engine.post(url, dvc_timeline_point_parameters.to_dict(dirty=True) if dvc_timeline_point_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def disable(engine, ref):
    """
    Disable this application container.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_3.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_3_3.web.objects.DVCAppli
        cationContainer.DVCApplicationContainer` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/container/%s/disable" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

