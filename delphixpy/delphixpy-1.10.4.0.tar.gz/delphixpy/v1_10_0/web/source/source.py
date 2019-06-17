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
Package "source"
"""
API_VERSION = "1.10.0"

from delphixpy.v1_10_0.web.source import operationTemplate
try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Source object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_0.web.vo.Source`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Source'], returns_list=False, raw_result=raw_result)

def get_all(engine, repository=None, database=None, include_hosts=None, all_sources=None, environment=None, config=None):
    """
    Lists sources on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param repository: List sources associated with the given source repository
        reference.
    :type repository: ``TEXT_TYPE``
    :param database: List visible sources associated with the given container
        reference. Visible sources are of type LINKED or VIRTUAL.
    :type database: ``TEXT_TYPE``
    :param include_hosts: Whether to include the list of hosts for each source
        in the response.
    :type include_hosts: ``bool``
    :param all_sources: List all sources associated with the given source
        container reference.
    :type all_sources: ``bool``
    :param environment: List sources associated with the given source
        environment reference.
    :type environment: ``TEXT_TYPE``
    :param config: List visible sources associated with the given sourceconfig
        reference. Visible sources are of type LINKED or VIRTUAL.
    :type config: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_10_0.web.vo.Source`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source"
    query_params = {"repository": repository, "database": database, "includeHosts": include_hosts, "allSources": all_sources, "environment": environment, "config": config}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Source'], returns_list=True, raw_result=raw_result)

def update(engine, ref, source=None):
    """
    Update the specified Source object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param source: Payload object.
    :type source: :py:class:`v1_10_0.web.vo.Source`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s" % ref
    response = engine.post(url, source.to_dict(dirty=True) if source else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable(engine, ref, source_enable_parameters=None):
    """
    Enables the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_enable_parameters: Payload object.
    :type source_enable_parameters:
        :py:class:`v1_10_0.web.vo.SourceEnableParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s/enable" % ref
    response = engine.post(url, source_enable_parameters.to_dict(dirty=True) if source_enable_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def populate(engine, ref, fraction_plug_parameters):
    """
    Add a TimeFlow to a warehouse source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param fraction_plug_parameters: Payload object.
    :type fraction_plug_parameters:
        :py:class:`v1_10_0.web.vo.FractionPlugParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s/populate" % ref
    response = engine.post(url, fraction_plug_parameters.to_dict(dirty=True) if fraction_plug_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def stop(engine, ref, source_stop_parameters=None):
    """
    Stops the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_stop_parameters: Payload object.
    :type source_stop_parameters:
        :py:class:`v1_10_0.web.vo.SourceStopParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s/stop" % ref
    response = engine.post(url, source_stop_parameters.to_dict(dirty=True) if source_stop_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def disable(engine, ref, source_disable_parameters=None):
    """
    Disables the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_disable_parameters: Payload object.
    :type source_disable_parameters:
        :py:class:`v1_10_0.web.vo.SourceDisableParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s/disable" % ref
    response = engine.post(url, source_disable_parameters.to_dict(dirty=True) if source_disable_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def start(engine, ref, source_start_parameters=None):
    """
    Starts the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_start_parameters: Payload object.
    :type source_start_parameters:
        :py:class:`v1_10_0.web.vo.SourceStartParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s/start" % ref
    response = engine.post(url, source_start_parameters.to_dict(dirty=True) if source_start_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def upgrade(engine, ref, source_upgrade_parameters=None):
    """
    Upgrades the given source.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_0.web.objects.Source.Source` object
    :type ref: ``str``
    :param source_upgrade_parameters: Payload object.
    :type source_upgrade_parameters:
        :py:class:`v1_10_0.web.vo.SourceUpgradeParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/source/%s/upgrade" % ref
    response = engine.post(url, source_upgrade_parameters.to_dict(dirty=True) if source_upgrade_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

