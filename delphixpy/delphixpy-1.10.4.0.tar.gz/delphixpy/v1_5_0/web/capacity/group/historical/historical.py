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
Package "capacity.group.historical"
"""
API_VERSION = "1.5.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_5_0 import response_validator

def get_all(engine, end_date=None, group=None, resolution=None, start_date=None):
    """
    Lists historical capacity data for a particular group.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_0.delphix_engine.DelphixEngine`
    :param end_date: Latest date for which to list data.
    :type end_date: ``TEXT_TYPE``
    :param group: The group to list data for.
    :type group: ``TEXT_TYPE``
    :param resolution: The time range each datapoint should represent, measured
        in seconds. This parameter is only meaningful if a group is specified.
    :type resolution: ``int``
    :param start_date: Earliest date for which to list data.
    :type start_date: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_5_0.web.vo.HistoricalGroupCapacityData`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/capacity/group/historical"
    query_params = {"group": group, "endDate": end_date, "resolution": resolution, "startDate": start_date}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'HistoricalGroupCapacityData'], returns_list=True, raw_result=raw_result)

