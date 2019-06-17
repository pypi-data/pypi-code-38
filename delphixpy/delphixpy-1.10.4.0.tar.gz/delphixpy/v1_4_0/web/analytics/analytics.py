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
Package "analytics"
"""
API_VERSION = "1.4.0"

from delphixpy.v1_4_0.web.analytics import statistic
try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_4_0 import response_validator

def create(engine, statistic_slice=None):
    """
    Create a new StatisticSlice object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param statistic_slice: Payload object.
    :type statistic_slice: :py:class:`v1_4_0.web.vo.StatisticSlice`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics"
    response = engine.post(url, statistic_slice.to_dict(dirty=True) if statistic_slice else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified StatisticSlice object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_4_0.web.vo.StatisticSlice`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'StatisticSlice'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Returns a list of statistics in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_4_0.web.vo.StatisticSlice`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'StatisticSlice'], returns_list=True, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified StatisticSlice object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def remember_range(engine, ref, time_range_parameters):
    """
    Prevents data from being deleted automatically.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    :param time_range_parameters: Payload object.
    :type time_range_parameters: :py:class:`v1_4_0.web.vo.TimeRangeParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s/rememberRange" % ref
    response = engine.post(url, time_range_parameters.to_dict(dirty=True) if time_range_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def pause(engine, ref):
    """
    Pauses the collection of data for this slice.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s/pause" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def get_data(engine, ref, number_of_datapoints=None, resolution=None, start_time=None, end_time=None):
    """
    Returns data for the specified time range.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    :param number_of_datapoints: The maximum number of datapoints to split the
        given time range into. Using this parameter requires that you supply a
        startTime parameter.
    :type number_of_datapoints: ``int``
    :param resolution: The time range each datapoint should represent, measured
        in seconds.
    :type resolution: ``int``
    :param start_time: None
    :type start_time: ``TEXT_TYPE``
    :param end_time: None
    :type end_time: ``TEXT_TYPE``
    :rtype: :py:class:`v1_4_0.web.vo.DatapointSet`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s/getData" % ref
    query_params = {"numberOfDatapoints": number_of_datapoints, "resolution": resolution, "startTime": start_time, "endTime": end_time}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'DatapointSet'], returns_list=False, raw_result=raw_result)

def stop_remembering_range(engine, ref, time_range_parameters):
    """
    Allows saved data to be deleted automatically if it is getting old.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    :param time_range_parameters: Payload object.
    :type time_range_parameters: :py:class:`v1_4_0.web.vo.TimeRangeParameters`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s/stopRememberingRange" % ref
    response = engine.post(url, time_range_parameters.to_dict(dirty=True) if time_range_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def resume(engine, ref):
    """
    Resumes the collection of data for this slice.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_4_0.web.objects.StatisticSlice.StatisticSlice`
        object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/%s/resume" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

