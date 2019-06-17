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
Package "audit"
"""
API_VERSION = "1.3.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_3_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified AuditEvent object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_3_1.web.objects.AuditEvent.AuditEvent` object
    :type ref: ``str``
    :rtype: :py:class:`v1_3_1.web.vo.AuditEvent`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/audit/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'AuditEvent'], returns_list=False, raw_result=raw_result)

def get_all(engine, to_date=None, page_offset=None, from_date=None, page_size=None):
    """
    Retrieve a historical log of audit events.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_3_1.delphix_engine.DelphixEngine`
    :param to_date: End date for the search. Only events on or before this date
        are included.
    :type to_date: ``TEXT_TYPE``
    :param page_offset: Offset within event list, in units of pageSize chunks.
    :type page_offset: ``int``
    :param from_date: Start date for the search. Only events on or after this
        date are included.
    :type from_date: ``TEXT_TYPE``
    :param page_size: Limit the number of events returned.
    :type page_size: ``int``
    :rtype: ``list`` of :py:class:`v1_3_1.web.vo.AuditEvent`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/audit"
    query_params = {"toDate": to_date, "pageOffset": page_offset, "fromDate": from_date, "pageSize": page_size}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'AuditEvent'], returns_list=True, raw_result=raw_result)

