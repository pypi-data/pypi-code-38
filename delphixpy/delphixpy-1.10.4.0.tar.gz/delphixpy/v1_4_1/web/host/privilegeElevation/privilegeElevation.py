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
Package "host.privilegeElevation"
"""
API_VERSION = "1.4.1"

from delphixpy.v1_4_1 import response_validator

def get(engine):
    """
    Retrieve the specified HostPrivilegeElevationSettings object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_4_1.web.vo.HostPrivilegeElevationSettings`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'HostPrivilegeElevationSettings'], returns_list=False, raw_result=raw_result)

def set(engine, host_privilege_elevation_settings=None):
    """
    Update the specified HostPrivilegeElevationSettings object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_4_1.delphix_engine.DelphixEngine`
    :param host_privilege_elevation_settings: Payload object.
    :type host_privilege_elevation_settings:
        :py:class:`v1_4_1.web.vo.HostPrivilegeElevationSettings`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/host/privilegeElevation"
    response = engine.post(url, host_privilege_elevation_settings.to_dict(dirty=True) if host_privilege_elevation_settings else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

