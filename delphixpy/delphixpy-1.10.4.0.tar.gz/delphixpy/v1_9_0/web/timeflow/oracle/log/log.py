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
Package "timeflow.oracle.log"
"""
API_VERSION = "1.9.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_9_0 import response_validator

def get_all(engine, to_date=None, page_offset=None, page_size=None, database=None, timeflow=None, from_scn=None, from_date=None, snapshot=None, to_scn=None, missing=None):
    """
    Returns a list of fetched or missing Oracle logs for a database, TimeFlow
    or snapshot. The logs are returned in ascending order by TimeFlow, SCN.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param to_date: Return logs created before than this date.
    :type to_date: ``TEXT_TYPE``
    :param page_offset: Page offset within log list, in units of pageSize
        chunks.
    :type page_offset: ``int``
    :param page_size: Limit the number of logs returned.
    :type page_size: ``int``
    :param database: Return logs on all TimeFlows associated with the
        container. This option is mutually exclusive with the "TimeFlow" and
        "snapshot" options.
    :type database: ``TEXT_TYPE``
    :param timeflow: Return logs in the specified TimeFlow. This option is
        mutually exclusive with the "snapshot" and "database" options.
    :type timeflow: ``TEXT_TYPE``
    :param from_scn: Return logs with SCNs greater than or equal to this value.
    :type from_scn: ``TEXT_TYPE``
    :param from_date: Return logs created after this date.
    :type from_date: ``TEXT_TYPE``
    :param snapshot: Return logs for the specified snapshot up to the next
        snapshot. This option is mutually exclusive with the "TimeFlow" and
        "database" options.
    :type snapshot: ``TEXT_TYPE``
    :param to_scn: Return logs with SCNs less than or equal to this value.
    :type to_scn: ``TEXT_TYPE``
    :param missing: Only return the missing logs.
    :type missing: ``bool``
    :rtype: ``list`` of :py:class:`v1_9_0.web.vo.OracleTimeflowLog`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/oracle/log"
    query_params = {"toDate": to_date, "pageOffset": page_offset, "pageSize": page_size, "fromScn": from_scn, "timeflow": timeflow, "database": database, "fromDate": from_date, "snapshot": snapshot, "toScn": to_scn, "missing": missing}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OracleTimeflowLog'], returns_list=True, raw_result=raw_result)

def fetch(engine, log_fetch_ssh):
    """
    Manually fetch log files to repair a portion of a TimeFlow.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param log_fetch_ssh: Payload object.
    :type log_fetch_ssh: :py:class:`v1_9_0.web.vo.LogFetchSSH`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/timeflow/oracle/log/fetch"
    response = engine.post(url, log_fetch_ssh.to_dict(dirty=True) if log_fetch_ssh else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

