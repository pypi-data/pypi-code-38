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
Package "replication.sourcestate"
"""
API_VERSION = "1.7.1"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_7_1 import response_validator

def get(engine, ref):
    """
    Retrieve the specified ReplicationSourceState object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_7_1.web.objects.Replicat
        ionSourceState.ReplicationSourceState` object
    :type ref: ``str``
    :rtype: :py:class:`v1_7_1.web.vo.ReplicationSourceState`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/replication/sourcestate/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'ReplicationSourceState'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List ReplicationSourceState objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_7_1.web.vo.ReplicationSourceState`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/replication/sourcestate"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'ReplicationSourceState'], returns_list=True, raw_result=raw_result)

def get_by_spec(engine, spec=None):
    """
    Find the replication source state associated with a given replication spec.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_7_1.delphix_engine.DelphixEngine`
    :param spec: Replication spec object reference.
    :type spec: ``TEXT_TYPE``
    :rtype: :py:class:`v1_7_1.web.vo.ReplicationSourceState`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/replication/sourcestate/getBySpec"
    query_params = {"spec": spec}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'ReplicationSourceState'], returns_list=False, raw_result=raw_result)

