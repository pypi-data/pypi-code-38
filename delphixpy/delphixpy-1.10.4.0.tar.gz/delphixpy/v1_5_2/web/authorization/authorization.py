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
Package "authorization"
"""
API_VERSION = "1.5.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_5_2 import response_validator

def create(engine, authorization=None):
    """
    Create a new Authorization object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param authorization: Payload object.
    :type authorization: :py:class:`v1_5_2.web.vo.Authorization`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/authorization"
    response = engine.post(url, authorization.to_dict(dirty=True) if authorization else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified Authorization object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_2.web.objects.Authorization.Authorization`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_5_2.web.vo.Authorization`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/authorization/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Authorization'], returns_list=False, raw_result=raw_result)

def get_all(engine, target=None, effective=None, user=None):
    """
    Lists authorizations granted in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param target: Lists the permissions granted on the specified object.
    :type target: ``TEXT_TYPE``
    :param effective: Also return inherited authorizations.
    :type effective: ``TEXT_TYPE``
    :param user: Lists permissions granted to the specified user.
    :type user: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_5_2.web.vo.Authorization`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/authorization"
    query_params = {"target": target, "effective": effective, "user": user}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Authorization'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified Authorization object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_2.web.objects.Authorization.Authorization`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/authorization/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def filter_by_permission(engine, auth_filter_parameters):
    """
    Filter a set of objects for which the user has the specified permission.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param auth_filter_parameters: Payload object.
    :type auth_filter_parameters:
        :py:class:`v1_5_2.web.vo.AuthFilterParameters`
    :rtype: :py:class:`v1_5_2.web.vo.AuthFilterResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/authorization/filterByPermission"
    response = engine.post(url, auth_filter_parameters.to_dict(dirty=True) if auth_filter_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'AuthFilterResult'], returns_list=False, raw_result=raw_result)

