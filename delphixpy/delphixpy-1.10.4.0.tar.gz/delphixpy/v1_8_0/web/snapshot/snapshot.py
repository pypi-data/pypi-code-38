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
Package "snapshot"
"""
API_VERSION = "1.8.0"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_8_0 import response_validator

def get(engine, ref):
    """
    Retrieve the specified TimeflowSnapshot object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_0.web.objects.TimeflowSnapshot.TimeflowSnapsh
        ot` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_0.web.vo.TimeflowSnapshot`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/snapshot/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TimeflowSnapshot'], returns_list=False, raw_result=raw_result)

def get_all(engine, to_date=None, page_size=None, database=None, timeflow=None, from_date=None, traverse_timeflows=None):
    """
    Returns a list of snapshots on the system or within a particular object. By
    default, all snapshots within the domain are listed.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param to_date: End date to use for filtering out results.
    :type to_date: ``TEXT_TYPE``
    :param page_size: Limit the number of snapshots returned.
    :type page_size: ``int``
    :param database: Restrict snapshots to those within a TimeFlow of the
        specified database. This option is mutually exclusive with the
        "TimeFlow" option.
    :type database: ``TEXT_TYPE``
    :param timeflow: Restrict snapshots to those within the specified TimeFlow.
        This option is mutually exclusive with the "database" option.
    :type timeflow: ``TEXT_TYPE``
    :param from_date: Start date to use for filtering out results.
    :type from_date: ``TEXT_TYPE``
    :param traverse_timeflows: Whether to restrict snapshots to those in the
        current TimeFlow and in parent TimeFlows older than the branch point.
        This option is only used with the "database" option. The default
        behavior is false, i.e. show all snapshots.
    :type traverse_timeflows: ``bool``
    :rtype: ``list`` of :py:class:`v1_8_0.web.vo.TimeflowSnapshot`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/snapshot"
    query_params = {"toDate": to_date, "pageSize": page_size, "traverseTimeflows": traverse_timeflows, "timeflow": timeflow, "database": database, "fromDate": from_date}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'TimeflowSnapshot'], returns_list=True, raw_result=raw_result)

def update(engine, ref, timeflow_snapshot=None):
    """
    Update the specified TimeflowSnapshot object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_0.web.objects.TimeflowSnapshot.TimeflowSnapsh
        ot` object
    :type ref: ``str``
    :param timeflow_snapshot: Payload object.
    :type timeflow_snapshot: :py:class:`v1_8_0.web.vo.TimeflowSnapshot`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/snapshot/%s" % ref
    response = engine.post(url, timeflow_snapshot.to_dict(dirty=True) if timeflow_snapshot else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified TimeflowSnapshot object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_0.web.objects.TimeflowSnapshot.TimeflowSnapsh
        ot` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/snapshot/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def timeflow_range(engine, ref, traverse_timeflows=None):
    """
    Return the provisionable TimeFlow range based on a specific snapshot.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_8_0.web.objects.TimeflowSnapshot.TimeflowSnapsh
        ot` object
    :type ref: ``str``
    :param traverse_timeflows: Whether to restrict the range to the branch
        point of the child TimeFlow. The default behavior is false.
    :type traverse_timeflows: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/snapshot/%s/timeflowRange" % ref
    query_params = {"traverseTimeflows": traverse_timeflows}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def space(engine, snapshot_space_parameters):
    """
    Returns the space used by the specified snapshot space parameters.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param snapshot_space_parameters: Payload object.
    :type snapshot_space_parameters:
        :py:class:`v1_8_0.web.vo.SnapshotSpaceParameters`
    :rtype: :py:class:`v1_8_0.web.vo.SnapshotSpaceResult`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/snapshot/space"
    response = engine.post(url, snapshot_space_parameters.to_dict(dirty=True) if snapshot_space_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SnapshotSpaceResult'], returns_list=False, raw_result=raw_result)

