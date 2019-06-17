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
Package "environment.oracle.clusternode"
"""
API_VERSION = "1.10.4"

try:
    from urllib import urlencode 
except ImportError:
    from urllib.parse import urlencode 
from delphixpy.v1_10_4 import response_validator

def create(engine, oracle_cluster_node_create_parameters):
    """
    Create a new OracleClusterNode object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param oracle_cluster_node_create_parameters: Payload object.
    :type oracle_cluster_node_create_parameters:
        :py:class:`v1_10_4.web.vo.OracleClusterNodeCreateParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/clusternode"
    response = engine.post(url, oracle_cluster_node_create_parameters.to_dict(dirty=True) if oracle_cluster_node_create_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified OracleClusterNode object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_10_4.web.objects.OracleC
        lusterNode.OracleClusterNode` object
    :type ref: ``str``
    :rtype: :py:class:`v1_10_4.web.vo.OracleClusterNode`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/clusternode/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OracleClusterNode'], returns_list=False, raw_result=raw_result)

def get_all(engine, cluster=None):
    """
    Returns a list of host nodes filtered by cluster.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param cluster: The cluster to filter by.
    :type cluster: ``TEXT_TYPE``
    :rtype: ``list`` of :py:class:`v1_10_4.web.vo.OracleClusterNode`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/clusternode"
    query_params = {"cluster": cluster}
    query_dct = {k: query_params[k] for k in query_params if query_params[k] is not None}
    if query_dct:
        url_params = urlencode(query_dct)
        url += "?%s" % url_params
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'OracleClusterNode'], returns_list=True, raw_result=raw_result)

def update(engine, ref, oracle_cluster_node=None):
    """
    Update the specified OracleClusterNode object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_10_4.web.objects.OracleC
        lusterNode.OracleClusterNode` object
    :type ref: ``str``
    :param oracle_cluster_node: Payload object.
    :type oracle_cluster_node: :py:class:`v1_10_4.web.vo.OracleClusterNode`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/clusternode/%s" % ref
    response = engine.post(url, oracle_cluster_node.to_dict(dirty=True) if oracle_cluster_node else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified OracleClusterNode object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_4.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_10_4.web.objects.OracleC
        lusterNode.OracleClusterNode` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/environment/oracle/clusternode/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

