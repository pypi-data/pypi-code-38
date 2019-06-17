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
Package "sourceconfig"
"""
API_VERSION = "1.6.0"

from delphixpy.v1_6_0.web.sourceconfig import oracle
try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_6_0 import response_validator

def create(engine, source_config=None):
    """
    Create a new SourceConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param source_config: Payload object.
    :type source_config: :py:class:`v1_6_0.web.vo.SourceConfig`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig"
    response = engine.post(url, source_config.to_dict(dirty=True) if source_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SourceConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_0.web.objects.SourceConfig.SourceConfig`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_6_0.web.vo.SourceConfig`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SourceConfig'], returns_list=False, raw_result=raw_result)

def get_all(engine, environment=None, repository=None):
    """
    Returns a list of source configs within the repository or the environment.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param environment: Restrict source configs to those belonging to the
        specified environment. This option is mutually exclusive with all other
        options.
    :type environment: ``TEXT_TYPE``
    :param repository: Restrict source configs to those belonging to the
        specified repository. This option is mutually exclusive with all other
        options.
    :type repository: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_6_0.web.vo.SourceConfig`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig"
    query_params = {"environment": environment, "repository": repository}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SourceConfig'], returns_list=True, raw_result=raw_result)

def update(engine, ref, source_config=None):
    """
    Update the specified SourceConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_0.web.objects.SourceConfig.SourceConfig`
        object
    :type ref: ``str``
    :param source_config: Payload object.
    :type source_config: :py:class:`v1_6_0.web.vo.SourceConfig`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig/%s" % ref
    response = engine.post(url, source_config.to_dict(dirty=True) if source_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SourceConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_0.web.objects.SourceConfig.SourceConfig`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def validate_credentials(engine, ref, source_config_connectivity):
    """
    Tests the validity of the supplied database credentials, returning an error
    if unable to connect to the database.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_0.web.objects.SourceConfig.SourceConfig`
        object
    :type ref: ``str``
    :param source_config_connectivity: Payload object.
    :type source_config_connectivity:
        :py:class:`v1_6_0.web.vo.SourceConfigConnectivity`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/sourceconfig/%s/validateCredentials" % ref
    response = engine.post(url, source_config_connectivity.to_dict(dirty=True) if source_config_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

