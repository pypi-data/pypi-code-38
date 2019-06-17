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
Package "connectivity"
"""
API_VERSION = "1.5.2"

from delphixpy.v1_5_2 import response_validator

def connector(engine, connector_connectivity=None):
    """
    Tests whether the given host is accessible over Delphix Connector protocol
    with the provided credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param connector_connectivity: Payload object.
    :type connector_connectivity:
        :py:class:`v1_5_2.web.vo.ConnectorConnectivity`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/connector"
    response = engine.post(url, connector_connectivity.to_dict(dirty=True) if connector_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def jdbc(engine, jdbc_connectivity=None):
    """
    Tests whether the given database is accessible over JDBC with the provided
    credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param jdbc_connectivity: Payload object.
    :type jdbc_connectivity: :py:class:`v1_5_2.web.vo.JDBCConnectivity`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/jdbc"
    response = engine.post(url, jdbc_connectivity.to_dict(dirty=True) if jdbc_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def ssh(engine, ssh_connectivity=None):
    """
    Tests whether the given host is accessible over SSH with the provided
    credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_2.delphix_engine.DelphixEngine`
    :param ssh_connectivity: Payload object.
    :type ssh_connectivity: :py:class:`v1_5_2.web.vo.SSHConnectivity`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/ssh"
    response = engine.post(url, ssh_connectivity.to_dict(dirty=True) if ssh_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

