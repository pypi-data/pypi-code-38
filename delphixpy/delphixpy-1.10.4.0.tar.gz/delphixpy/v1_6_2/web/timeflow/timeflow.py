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
Package "timeflow"
"""
API_VERSION = "1.6.2"

from delphixpy.v1_6_2.web.timeflow import oracle
try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_6_2 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Timeflow object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Timeflow.Timeflow` object
    :type ref: ``str``
    :rtype: :py:class:`v1_6_2.web.vo.Timeflow`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Timeflow'], returns_list=False, raw_result=raw_result)

def get_all(engine, database=None):
    """
    List Timeflow objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param database: List only TimeFlows within this database.
    :type database: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_6_2.web.vo.Timeflow`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow"
    query_params = {"database": database}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Timeflow'], returns_list=True, raw_result=raw_result)

def update(engine, ref, timeflow=None):
    """
    Update the specified Timeflow object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Timeflow.Timeflow` object
    :type ref: ``str``
    :param timeflow: Payload object.
    :type timeflow: :py:class:`v1_6_2.web.vo.Timeflow`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/%s" % ref
    response = engine.post(url, timeflow.to_dict(dirty=True) if timeflow else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def repair(engine, ref, timeflow_repair_parameters=None):
    """
    Manually fetch log files to repair a portion of a TimeFlow.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Timeflow.Timeflow` object
    :type ref: ``str``
    :param timeflow_repair_parameters: Payload object.
    :type timeflow_repair_parameters:
        :py:class:`v1_6_2.web.vo.TimeflowRepairParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/%s/repair" % ref
    response = engine.post(url, timeflow_repair_parameters.to_dict(dirty=True) if timeflow_repair_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def timeflow_ranges(engine, ref, timeflow_range_parameters=None):
    """
    Fetches TimeFlow ranges in between the specified start and end locations.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Timeflow.Timeflow` object
    :type ref: ``str``
    :param timeflow_range_parameters: Payload object.
    :type timeflow_range_parameters:
        :py:class:`v1_6_2.web.vo.TimeflowRangeParameters`
    :rtype: ``list`` of :py:class:`v1_6_2.web.vo.TimeflowRange`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/%s/timeflowRanges" % ref
    response = engine.post(url, timeflow_range_parameters.to_dict(dirty=True) if timeflow_range_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TimeflowRange'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Deletes a TimeFlow.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_2.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_2.web.objects.Timeflow.Timeflow` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

