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
Package "fault.effect"
"""
API_VERSION = "1.10.4"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_4 import response_validator

def get(engine, ref):
    """
    Retrieve the specified FaultEffect object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_10_4.web.objects.FaultEffect.FaultEffect`
        object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_4.web.vo.FaultEffect`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/fault/effect/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'FaultEffect'], returns_list=False, raw_result=raw_result)

def get_all(engine, root_cause=None, target=None, severity=None, bundle_id=None):
    """
    Returns the list of all the fault effects that match the given criteria.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param root_cause: The reference to the fault which is the root cause of
        the fault effect.
    :type root_cause: ``TEXT_TYPE``
    :param target: The reference to the Delphix user-visible object associated
        with the fault effect.
    :type target: ``TEXT_TYPE``
    :param severity: The impact of the fault effect on the system: CRITICAL or
        WARNING. *(permitted values: CRITICAL, WARNING)*
    :type severity: ``TEXT_TYPE``
    :param bundle_id: A unique dot delimited identifier associated with the
        fault effect.
    :type bundle_id: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_10_4.web.vo.FaultEffect`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/fault/effect"
    query_params = {"rootCause": root_cause, "bundleID": bundle_id, "target": target, "severity": severity}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'FaultEffect'], returns_list=True, raw_result=raw_result)

