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
Package "usage"
"""
API_VERSION = "1.10.3"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_3 import response_validator

def aggregate_ingested_size(engine, start_date=None, end_date=None):
    """
    Retrieve data pertaining to sum of the aggregate ingested size for each
    data source within a specified time range. If no start or end date is
    specified, it will return the ingested size for each data source from the
    last collection time until now.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_3.delphix_engine.DelphixEngine`
    :param start_date: Start time at which this information was sampled.
    :type start_date: ``TEXT_TYPE``
    :param end_date: End time at which this information was sampled.
    :type end_date: ``TEXT_TYPE``
    :rtype: :py:class:`v1_10_3.web.vo.EngineAggregateIngestedSize`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/usage/aggregateIngestedSize"
    query_params = {"startDate": start_date, "endDate": end_date}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'EngineAggregateIngestedSize'], returns_list=False, raw_result=raw_result)

