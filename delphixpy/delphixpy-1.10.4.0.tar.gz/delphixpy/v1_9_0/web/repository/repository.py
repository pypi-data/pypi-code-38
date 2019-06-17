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
Package "repository"
"""
API_VERSION = "1.9.0"

from delphixpy.v1_9_0.web.repository import template
try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_0 import response_validator

def create(engine, source_repository=None):
    """
    Create a new SourceRepository object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param source_repository: Payload object.
    :type source_repository: :py:class:`v1_9_0.web.vo.SourceRepository`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/repository"
    response = engine.post(url, source_repository.to_dict(dirty=True) if source_repository else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SourceRepository object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SourceRepository.SourceReposito
        ry` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_0.web.vo.SourceRepository`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/repository/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SourceRepository'], returns_list=False, raw_result=raw_result)

def get_all(engine, environment=None):
    """
    Returns a list of source repositories within the environment or the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param environment: Restrict source repositories belong to the specified
        environment.
    :type environment: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_9_0.web.vo.SourceRepository`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/repository"
    query_params = {"environment": environment}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SourceRepository'], returns_list=True, raw_result=raw_result)

def update(engine, ref, source_repository=None):
    """
    Update the specified SourceRepository object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SourceRepository.SourceReposito
        ry` object
    :type ref: ``str``
    :param source_repository: Payload object.
    :type source_repository: :py:class:`v1_9_0.web.vo.SourceRepository`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/repository/%s" % ref
    response = engine.post(url, source_repository.to_dict(dirty=True) if source_repository else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SourceRepository object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SourceRepository.SourceReposito
        ry` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/repository/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def compatible_repositories(engine, compatible_repositories_parameters):
    """
    Returns a list of repositories that match the specified parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param compatible_repositories_parameters: Payload object.
    :type compatible_repositories_parameters:
        :py:class:`v1_9_0.web.vo.CompatibleRepositoriesParameters`
    :rtype: :py:class:`v1_9_0.web.vo.CompatibleRepositoriesResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/repository/compatibleRepositories"
    response = engine.post(url, compatible_repositories_parameters.to_dict(dirty=True) if compatible_repositories_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'CompatibleRepositoriesResult'], returns_list=False, raw_result=raw_result)

