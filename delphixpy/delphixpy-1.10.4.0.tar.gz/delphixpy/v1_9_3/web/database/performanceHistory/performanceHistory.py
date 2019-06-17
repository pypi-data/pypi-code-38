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
Package "database.performanceHistory"
"""
API_VERSION = "1.9.3"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_3 import response_validator

def get_all(engine, sampling_interval=None, to_date=None, from_date=None):
    """
    Reports the utilization of all containers during a particular period of
    time.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_3.delphix_engine.DelphixEngine`
    :param sampling_interval: The interval at which data is to be sampled,
        measured in seconds.
    :type sampling_interval: ``float``
    :param to_date: The latest date for which container utilization statistics
        will be reported.
    :type to_date: ``TEXT_TYPE``
    :param from_date: The earliest date for which container utilization
        statistics will be reported.
    :type from_date: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_9_3.web.vo.ContainerUtilization`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/database/performanceHistory"
    query_params = {"samplingInterval": sampling_interval, "toDate": to_date, "fromDate": from_date}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'ContainerUtilization'], returns_list=True, raw_result=raw_result)

