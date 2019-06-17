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
Package "analytics.statistic"
"""
API_VERSION = "1.6.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_6_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified Statistic object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_6_0.web.objects.Statistic.Statistic` object
    :type ref: ``str``
    :rtype: :py:class:`v1_6_0.web.vo.Statistic`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/statistic/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Statistic'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Returns a list of statistics in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_6_0.web.vo.Statistic`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/statistic"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Statistic'], returns_list=True, raw_result=raw_result)

def show_axes(engine, statistic_type=None):
    """
    Returns the set of axes for a statistic type.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param statistic_type: None
    :type statistic_type: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_6_0.web.vo.StatisticAxis`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/analytics/statistic/showAxes"
    query_params = {"statisticType": statistic_type}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'StatisticAxis'], returns_list=True, raw_result=raw_result)

