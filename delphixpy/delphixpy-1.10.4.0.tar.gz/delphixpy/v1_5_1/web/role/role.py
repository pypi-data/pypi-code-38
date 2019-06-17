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
Package "role"
"""
API_VERSION = "1.5.1"

from delphixpy.v1_5_1 import response_validator

def create(engine, role=None):
    """
    Create a new Role object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :param role: Payload object.
    :type role: :py:class:`v1_5_1.web.vo.Role`
    :rtype: ``TEXT_TYPE``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role"
    response = engine.post(url, role.to_dict(dirty=True) if role else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TEXT_TYPE'], returns_list=False, raw_result=raw_result)

def get(engine, ref):
    """
    Retrieve the specified Role object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_1.web.objects.Role.Role` object
    :type ref: ``str``
    :rtype: :py:class:`v1_5_1.web.vo.Role`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role/%s" % ref
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Role'], returns_list=False, raw_result=raw_result)

def get_all(engine):
    """
    Lists roles available in the system.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :rtype: ``list`` of :py:class:`v1_5_1.web.vo.Role`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Role'], returns_list=True, raw_result=raw_result)

def update(engine, ref, role=None):
    """
    Update the specified Role object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_1.web.objects.Role.Role` object
    :type ref: ``str``
    :param role: Payload object.
    :type role: :py:class:`v1_5_1.web.vo.Role`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role/%s" % ref
    response = engine.post(url, role.to_dict(dirty=True) if role else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def delete(engine, ref):
    """
    Delete the specified Role object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :param ref: Reference to a
        :py:class:`delphixpy.v1_5_1.web.objects.Role.Role` object
    :type ref: ``str``
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role/%s/delete" % ref
    response = engine.post(url, None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def owner_role(engine):
    """
    Returns the owner role.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_5_1.web.vo.Role`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role/ownerRole"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Role'], returns_list=False, raw_result=raw_result)

def auditor_role(engine):
    """
    Returns the auditor role.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_5_1.web.vo.Role`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role/auditorRole"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Role'], returns_list=False, raw_result=raw_result)

def jet_stream_user_role(engine):
    """
    Returns the Jet Stream user role.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_5_1.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_5_1.web.vo.Role`
    """
    assert API_VERSION == engine.API_VERSION, "Wrong API version (%s) for parameter 'engine' (%s)" % (API_VERSION, engine.API_VERSION)
    url = "/resources/json/delphix/role/jetStreamUserRole"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=[u'Role'], returns_list=False, raw_result=raw_result)

