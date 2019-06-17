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
Package "dvc.datasource"
"""
API_VERSION = "1.3.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_3_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified DVCDataSource object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_0.web.objects.DVCDataSource.DVCDataSource`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_3_0.web.vo.DVCDataSource`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/datasource/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCDataSource'], returns_list=False, raw_result=raw_result)

def get_all(engine, application=None, container=None):
    """
    Lists the DVC data sources in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_0.delphix_engine.DelphixEngine`
    :param application: List the sources associated with the given application
        reference.
    :type application: ``TEXT_TYPE``
    :param container: List the source associated with the given container
        reference.
    :type container: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_3_0.web.vo.DVCDataSource`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/datasource"
    query_params = {"application": application, "container": container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCDataSource'], returns_list=True, raw_result=raw_result)

def update(engine, ref, dvc_data_source=None):
    """
    Update the specified DVCDataSource object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_0.web.objects.DVCDataSource.DVCDataSource`
        object
    :type ref: ``str``
    :param dvc_data_source: Payload object.
    :type dvc_data_source: :py:class:`v1_3_0.web.vo.DVCDataSource`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/datasource/%s" % ref
    response = engine.post(url, dvc_data_source.to_dict(dirty=True) if dvc_data_source else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def data_timestamps(engine, dvc_source_data_timestamp_parameters):
    """
    Given a point in time, returns the timestamps of the latest provisionable
    points, before the specified time, for each data source in the given
    application.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_0.delphix_engine.DelphixEngine`
    :param dvc_source_data_timestamp_parameters: Payload object.
    :type dvc_source_data_timestamp_parameters:
        :py:class:`v1_3_0.web.vo.DVCSourceDataTimestampParameters`
    :rtype: ``list`` of :py:class:`v1_3_0.web.vo.DVCSourceDataTimestamp`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/dvc/datasource/dataTimestamps"
    response = engine.post(url, dvc_source_data_timestamp_parameters.to_dict(dirty=True) if dvc_source_data_timestamp_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DVCSourceDataTimestamp'], returns_list=True, raw_result=raw_result)

