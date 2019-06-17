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
Package "jetstream.datasource"
"""
API_VERSION = "1.5.2"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_5_2 import response_validator

def get(engine, ref):
    """
    Retrieve the specified JSDataSource object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_2.web.objects.JSDataSource.JSDataSource`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_5_2.web.vo.JSDataSource`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/datasource/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSDataSource'], returns_list=False, raw_result=raw_result)

def get_all(engine, data_layout=None, container=None):
    """
    Lists the Jet Stream data sources in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param data_layout: List the sources associated with the given data layout
        reference.
    :type data_layout: ``TEXT_TYPE``
    :param container: List the source associated with the given container
        reference.
    :type container: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_5_2.web.vo.JSDataSource`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/datasource"
    query_params = {"dataLayout": data_layout, "container": container}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSDataSource'], returns_list=True, raw_result=raw_result)

def update(engine, ref, js_data_source=None):
    """
    Update the specified JSDataSource object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_2.web.objects.JSDataSource.JSDataSource`
        object
    :type ref: ``str``
    :param js_data_source: Payload object.
    :type js_data_source: :py:class:`v1_5_2.web.vo.JSDataSource`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/datasource/%s" % ref
    response = engine.post(url, js_data_source.to_dict(dirty=True) if js_data_source else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def data_timestamps(engine, js_source_data_timestamp_parameters):
    """
    Given a point in time, returns the timestamps of the latest provisionable
    points, before the specified time, for each data source in the given data
    layout.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param js_source_data_timestamp_parameters: Payload object.
    :type js_source_data_timestamp_parameters:
        :py:class:`v1_5_2.web.vo.JSSourceDataTimestampParameters`
    :rtype: ``list`` of :py:class:`v1_5_2.web.vo.JSSourceDataTimestamp`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/jetstream/datasource/dataTimestamps"
    response = engine.post(url, js_source_data_timestamp_parameters.to_dict(dirty=True) if js_source_data_timestamp_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'JSSourceDataTimestamp'], returns_list=True, raw_result=raw_result)

