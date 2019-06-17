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
Package "environment.oracle.listener"
"""
API_VERSION = "1.9.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_2 import response_validator

def create(engine, oracle_listener=None):
    """
    Create a new OracleListener object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param oracle_listener: Payload object.
    :type oracle_listener: :py:class:`v1_9_2.web.vo.OracleListener`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/listener"
    response = engine.post(url, oracle_listener.to_dict(dirty=True) if oracle_listener else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified OracleListener object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.OracleListener.OracleListener`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_2.web.vo.OracleListener`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/listener/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OracleListener'], returns_list=False, raw_result=raw_result)

def get_all(engine, environment=None, type=None):
    """
    Returns a list of listeners within the environment or the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param environment: Restrict listeners belonging to the specified
        environment.
    :type environment: ``TEXT_TYPE``
    :param type: Restrict listeners to type. *(permitted values:
        OracleNodeListener, OracleScanListener)*
    :type type: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_9_2.web.vo.OracleListener`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/listener"
    query_params = {"environment": environment, "type": type}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OracleListener'], returns_list=True, raw_result=raw_result)

def update(engine, ref, oracle_listener=None):
    """
    Update the specified OracleListener object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.OracleListener.OracleListener`
        object
    :type ref: ``str``
    :param oracle_listener: Payload object.
    :type oracle_listener: :py:class:`v1_9_2.web.vo.OracleListener`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/listener/%s" % ref
    response = engine.post(url, oracle_listener.to_dict(dirty=True) if oracle_listener else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified OracleListener object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_2.web.objects.OracleListener.OracleListener`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/listener/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

