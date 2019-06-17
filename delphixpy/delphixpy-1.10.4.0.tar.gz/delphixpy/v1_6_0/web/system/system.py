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
Package "system"
"""
API_VERSION = "1.6.0"

from delphixpy.v1_6_0.web.system import version
from delphixpy.v1_6_0 import response_validator

def get(engine):
    """
    Retrieve the specified SystemInfo object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_6_0.web.vo.SystemInfo`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'SystemInfo'], returns_list=False, raw_result=raw_result)

def set(engine, system_info=None):
    """
    Update the specified SystemInfo object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    :param system_info: Payload object.
    :type system_info: :py:class:`v1_6_0.web.vo.SystemInfo`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system"
    response = engine.post(url, system_info.to_dict(dirty=True) if system_info else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def enable_warehouse_feature(engine):
    """
    Enable the virtual warehouse feature.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/enableWarehouseFeature"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def reboot(engine):
    """
    Reboots the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/reboot"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def shutdown(engine):
    """
    Shuts down the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/shutdown"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def factory_reset(engine):
    """
    Resets the system to factory settings as after installation.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_6_0.delphix_engine.DelphixEngine`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/system/factoryReset"
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

