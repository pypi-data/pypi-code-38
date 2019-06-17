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
API_VERSION = "1.10.2"

from delphixpy.v1_10_2 import response_validator

def jdbc(engine, jdbc_connectivity=None):
    """
    Tests whether the given database is accessible over JDBC with the provided
    credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param jdbc_connectivity: Payload object.
    :type jdbc_connectivity: :py:class:`v1_10_2.web.vo.JDBCConnectivity`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/jdbc"
    response = engine.post(url, jdbc_connectivity.to_dict(dirty=True) if jdbc_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def commvault(engine, commvault_connectivity_parameters=None):
    """
    Tests whether the CommServe host is accessible from the given environment
    and Commvault agent.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param commvault_connectivity_parameters: Payload object.
    :type commvault_connectivity_parameters:
        :py:class:`v1_10_2.web.vo.CommvaultConnectivityParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/commvault"
    response = engine.post(url, commvault_connectivity_parameters.to_dict(dirty=True) if commvault_connectivity_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def netbackup(engine, netbackup_connectivity_parameters=None):
    """
    Tests whether the NetBackup master server is accessible from the given
    environment and NetBackup client.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param netbackup_connectivity_parameters: Payload object.
    :type netbackup_connectivity_parameters:
        :py:class:`v1_10_2.web.vo.NetbackupConnectivityParameters`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/netbackup"
    response = engine.post(url, netbackup_connectivity_parameters.to_dict(dirty=True) if netbackup_connectivity_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def dsp(engine, dsp_connectivity=None):
    """
    Tests whether the given host is accessible via DSP.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param dsp_connectivity: Payload object.
    :type dsp_connectivity: :py:class:`v1_10_2.web.vo.DspConnectivity`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/dsp"
    response = engine.post(url, dsp_connectivity.to_dict(dirty=True) if dsp_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def connector(engine, connector_connectivity=None):
    """
    Tests whether the given host is accessible over Delphix Connector protocol
    with the provided credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param connector_connectivity: Payload object.
    :type connector_connectivity:
        :py:class:`v1_10_2.web.vo.ConnectorConnectivity`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/connector"
    response = engine.post(url, connector_connectivity.to_dict(dirty=True) if connector_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def ssh(engine, ssh_connectivity=None):
    """
    Tests whether the given host is accessible over SSH with the provided
    credentials.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_10_2.delphix_engine.DelphixEngine`
    :param ssh_connectivity: Payload object.
    :type ssh_connectivity: :py:class:`v1_10_2.web.vo.SSHConnectivity`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/connectivity/ssh"
    response = engine.post(url, ssh_connectivity.to_dict(dirty=True) if ssh_connectivity else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

