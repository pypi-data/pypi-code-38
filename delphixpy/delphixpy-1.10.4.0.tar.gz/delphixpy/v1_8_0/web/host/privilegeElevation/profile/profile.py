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
Package "host.privilegeElevation.profile"
"""
API_VERSION = "1.8.0"

from delphixpy.v1_8_0 import response_validator

def create(engine, host_privilege_elevation_profile=None):
    """
    Create a new HostPrivilegeElevationProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param host_privilege_elevation_profile: Payload object.
    :type host_privilege_elevation_profile:
        :py:class:`v1_8_0.web.vo.HostPrivilegeElevationProfile`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profile"
    response = engine.post(url, host_privilege_elevation_profile.to_dict(dirty=True) if host_privilege_elevation_profile else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified HostPrivilegeElevationProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_8_0.web.objects.HostPriv
        ilegeElevationProfile.HostPrivilegeElevationProfile` object
    :type ref: ``str``
    :rtype: :py:class:`v1_8_0.web.vo.HostPrivilegeElevationProfile`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profile/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'HostPrivilegeElevationProfile'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    List HostPrivilegeElevationProfile objects on the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_8_0.web.vo.HostPrivilegeElevationProfile`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profile"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'HostPrivilegeElevationProfile'], returns_list=True, raw_result=raw_result)

def update(engine, ref, host_privilege_elevation_profile=None):
    """
    Update the specified HostPrivilegeElevationProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_8_0.web.objects.HostPriv
        ilegeElevationProfile.HostPrivilegeElevationProfile` object
    :type ref: ``str``
    :param host_privilege_elevation_profile: Payload object.
    :type host_privilege_elevation_profile:
        :py:class:`v1_8_0.web.vo.HostPrivilegeElevationProfile`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profile/%s" % ref
    response = engine.post(url, host_privilege_elevation_profile.to_dict(dirty=True) if host_privilege_elevation_profile else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified HostPrivilegeElevationProfile object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_8_0.delphix_engine.DelphixEngine`
    :param ref: Reference to a :py:class:`delphixpy.v1_8_0.web.objects.HostPriv
        ilegeElevationProfile.HostPrivilegeElevationProfile` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation/profile/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

