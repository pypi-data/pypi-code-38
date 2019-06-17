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
Package "service.snmp.manager"
"""
API_VERSION = "1.9.0"

from delphixpy.v1_9_0 import response_validator

def create(engine, snmp_manager=None):
    """
    Create a new SNMPManager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param snmp_manager: Payload object.
    :type snmp_manager: :py:class:`v1_9_0.web.vo.SNMPManager`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/snmp/manager"
    response = engine.post(url, snmp_manager.to_dict(dirty=True) if snmp_manager else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified SNMPManager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SNMPManager.SNMPManager` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_0.web.vo.SNMPManager`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/snmp/manager/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SNMPManager'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists SNMP managers in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_9_0.web.vo.SNMPManager`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/snmp/manager"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SNMPManager'], returns_list=True, raw_result=raw_result)

def update(engine, ref, snmp_manager=None):
    """
    Update the specified SNMPManager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SNMPManager.SNMPManager` object
    :type ref: ``str``
    :param snmp_manager: Payload object.
    :type snmp_manager: :py:class:`v1_9_0.web.vo.SNMPManager`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/snmp/manager/%s" % ref
    response = engine.post(url, snmp_manager.to_dict(dirty=True) if snmp_manager else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified SNMPManager object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SNMPManager.SNMPManager` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/snmp/manager/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def test(engine, ref):
    """
    Tests the ability to send an SNMP INFORM message to the manager (only
    applies when useInform is true).

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_9_0.web.objects.SNMPManager.SNMPManager` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/service/snmp/manager/%s/test" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

