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
Package "environment.user"
"""
API_VERSION = "1.7.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_7_1 import response_validator

def create(engine, environment_user=None):
    """
    Create a new EnvironmentUser object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param environment_user: Payload object.
    :type environment_user: :py:class:`v1_7_1.web.vo.EnvironmentUser`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/user"
    response = engine.post(url, environment_user.to_dict(dirty=True) if environment_user else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified EnvironmentUser object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.EnvironmentUser.EnvironmentUser
        ` object
    :type ref: ``str``
    :rtype: :py:class:`v1_7_1.web.vo.EnvironmentUser`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/user/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'EnvironmentUser'], returns_list=False, raw_result=raw_result)

def get_all(engine, environment=None):
    """
    Returns the list of all environment users in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param environment: Limit results to users within the given environment.
    :type environment: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_7_1.web.vo.EnvironmentUser`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/user"
    query_params = {"environment": environment}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'EnvironmentUser'], returns_list=True, raw_result=raw_result)

def update(engine, ref, environment_user=None):
    """
    Update the specified EnvironmentUser object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.EnvironmentUser.EnvironmentUser
        ` object
    :type ref: ``str``
    :param environment_user: Payload object.
    :type environment_user: :py:class:`v1_7_1.web.vo.EnvironmentUser`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/user/%s" % ref
    response = engine.post(url, environment_user.to_dict(dirty=True) if environment_user else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref, delete_parameters=None):
    """
    Delete the specified EnvironmentUser object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_7_1.web.objects.EnvironmentUser.EnvironmentUser
        ` object
    :type ref: ``str``
    :param delete_parameters: Payload object.
    :type delete_parameters: :py:class:`v1_7_1.web.vo.DeleteParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/user/%s/delete" % ref
    response = engine.post(url, delete_parameters.to_dict(dirty=True) if delete_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

