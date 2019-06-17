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
Package "host.privilegeElevation.profileScript"
"""
API_VERSION = "1.9.1"

from delphixpy.v1_9_1 import response_validator

def create(engine, host_privilege_elevation_profile_script=None):
    """
    Create a new HostPrivilegeElevationProfileScript object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param host_privilege_elevation_profile_script: Payload object.
    :type host_privilege_elevation_profile_script:
        :py:class:`v1_9_1.web.vo.HostPrivilegeElevationProfileScript`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profileScript"
    response = engine.post(url, host_privilege_elevation_profile_script.to_dict(dirty=True) if host_privilege_elevation_profile_script else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified HostPrivilegeElevationProfileScript object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_1.web.objects.HostPriv
        ilegeElevationProfileScript.HostPrivilegeElevationProfileScript` object
    :type ref: ``str``
    :rtype: :py:class:`v1_9_1.web.vo.HostPrivilegeElevationProfileScript`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profileScript/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'HostPrivilegeElevationProfileScript'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List HostPrivilegeElevationProfileScript objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of
        :py:class:`v1_9_1.web.vo.HostPrivilegeElevationProfileScript`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profileScript"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'HostPrivilegeElevationProfileScript'], returns_list=True, raw_result=raw_result)

def update(engine, ref, host_privilege_elevation_profile_script=None):
    """
    Update the specified HostPrivilegeElevationProfileScript object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_1.web.objects.HostPriv
        ilegeElevationProfileScript.HostPrivilegeElevationProfileScript` object
    :type ref: ``str``
    :param host_privilege_elevation_profile_script: Payload object.
    :type host_privilege_elevation_profile_script:
        :py:class:`v1_9_1.web.vo.HostPrivilegeElevationProfileScript`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profileScript/%s" % ref
    response = engine.post(url, host_privilege_elevation_profile_script.to_dict(dirty=True) if host_privilege_elevation_profile_script else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified HostPrivilegeElevationProfileScript object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_9_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_9_1.web.objects.HostPriv
        ilegeElevationProfileScript.HostPrivilegeElevationProfileScript` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profileScript/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

